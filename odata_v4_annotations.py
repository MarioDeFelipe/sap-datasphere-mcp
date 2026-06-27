"""OData V4 annotation extraction for SAP Datasphere consumption $metadata.

SAP Datasphere consumption $metadata is OData 4.0. The semantic info that
used to live in V2 ``sap:*`` attributes (``sap:label``, ``sap:aggregation-role``,
``sap:dimension``, ``sap:aggregation``, ``sap:unit``, ``sap:hierarchy``,
``sap:semantics``) now arrives as ``<Annotation Term="...">`` elements,
almost always in external ``<Annotations Target="<Schema>.<EntityType>/<Property>">``
blocks at the schema level (not inline children of ``<Property>``).

This module reads both forms and falls back to the legacy V2 attributes so any
still-V2 source keeps working. Kept dependency-free (stdlib only) so it can be
imported by the MCP server without pulling in heavy ETL deps.
"""

SAP_DATA_NS = 'http://www.sap.com/Protocols/SAPData'


def _term_suffix(term):
    """Local-name part of an annotation Term (after the last dot), lowercased.

    Matching by suffix is alias-agnostic: ``Common.Label`` and
    ``com.sap.vocabularies.Common.v1.Label`` both reduce to ``label``.
    """
    return term.rsplit('.', 1)[-1].lower() if term else ''


def _annotation_value(ann_el):
    """Pull a simple value out of an ``<Annotation>`` element.

    Order: ``String`` → ``Bool`` → ``EnumMember`` → element text → ``None``.
    Returns a Python ``bool`` for ``Bool``, ``str`` otherwise.
    """
    if 'String' in ann_el.attrib:
        return ann_el.get('String')
    if 'Bool' in ann_el.attrib:
        return ann_el.get('Bool', 'false').lower() == 'true'
    if 'EnumMember' in ann_el.attrib:
        return ann_el.get('EnumMember')
    return (ann_el.text or '').strip() or None


def _gather_annotations(prop_el, entity_type_name, schema_namespace, schema_el, namespaces):
    """Yield Annotation elements for a property: inline children + external schema-level blocks."""
    for ann in prop_el.findall('edm:Annotation', namespaces):
        yield ann
    if schema_el is None or not entity_type_name or not schema_namespace:
        return
    target_key = '{}.{}/{}'.format(
        schema_namespace, entity_type_name, prop_el.get('Name', ''),
    )
    for anns in schema_el.findall('edm:Annotations', namespaces):
        if anns.get('Target') == target_key:
            for ann in anns.findall('edm:Annotation', namespaces):
                yield ann


def extract_property_semantics(prop_el, entity_type_name, schema_namespace, schema_el, namespaces):
    """Read OData V4 SAP-vocabulary annotations for one ``<Property>``; V2 ``sap:*`` fallback.

    Returns a dict with these keys (all optional, ``None``/``False`` when absent):
    ``label``, ``is_dimension``, ``is_measure``, ``aggregation``,
    ``unit``, ``hierarchy``, ``semantics``, ``terms`` (raw Term list).
    """
    sem = {
        'label': None,
        'is_dimension': False,
        'is_measure': False,
        'aggregation': None,
        'unit': None,
        'hierarchy': None,
        'semantics': None,
        'terms': [],
    }

    for ann in _gather_annotations(prop_el, entity_type_name, schema_namespace, schema_el, namespaces):
        term = ann.get('Term', '')
        if not term:
            continue
        sem['terms'].append(term)
        suffix = _term_suffix(term)
        value = _annotation_value(ann)

        if suffix == 'label':
            if not sem['label'] and isinstance(value, str):
                sem['label'] = value
        elif suffix == 'dimension':
            if value is True or (isinstance(value, str) and value.lower() == 'true'):
                sem['is_dimension'] = True
        elif suffix in ('measure', 'ismeasure'):
            if value is True or (isinstance(value, str) and value.lower() == 'true'):
                sem['is_measure'] = True
        elif suffix == 'aggregationrole':
            low = (value or '').lower() if isinstance(value, str) else ''
            if 'dimension' in low:
                sem['is_dimension'] = True
            elif 'measure' in low:
                sem['is_measure'] = True
        elif suffix == 'defaultaggregation' and isinstance(value, str):
            sem['aggregation'] = sem['aggregation'] or value.rsplit('/', 1)[-1].lstrip('#')
        elif suffix in ('unit', 'isocurrency') and isinstance(value, str):
            sem['unit'] = sem['unit'] or value
        elif 'hierarchy' in suffix:
            sem['hierarchy'] = sem['hierarchy'] or value
        elif term.startswith('Common.') and 'semantic' in suffix and isinstance(value, str):
            sem['semantics'] = sem['semantics'] or value

    # Legacy V2 fallback — only fills fields still unset
    if sem['label'] is None:
        sem['label'] = prop_el.get('{{{}}}label'.format(SAP_DATA_NS))
    if not sem['is_dimension'] and prop_el.get('{{{}}}dimension'.format(SAP_DATA_NS)) == 'true':
        sem['is_dimension'] = True
    legacy_role = prop_el.get('{{{}}}aggregation-role'.format(SAP_DATA_NS))
    if legacy_role == 'dimension':
        sem['is_dimension'] = True
    elif legacy_role == 'measure':
        sem['is_measure'] = True
    legacy_agg = prop_el.get('{{{}}}aggregation'.format(SAP_DATA_NS))
    if legacy_agg:
        sem['is_measure'] = True
        sem['aggregation'] = sem['aggregation'] or legacy_agg
    if sem['unit'] is None:
        sem['unit'] = prop_el.get('{{{}}}unit'.format(SAP_DATA_NS))
    if sem['hierarchy'] is None:
        sem['hierarchy'] = prop_el.get('{{{}}}hierarchy'.format(SAP_DATA_NS))
    if sem['semantics'] is None:
        sem['semantics'] = prop_el.get('{{{}}}semantics'.format(SAP_DATA_NS))

    return sem


def make_semantics_extractor(root_el, namespaces):
    """Return a closure ``extract(prop_el, entity_type_el) -> semantics dict``.

    Builds an entity-type → (schema_el, schema_namespace) index once so the
    external ``<Annotations Target=…>`` lookup is cheap per property call.
    """
    index = {}
    for schema_el in root_el.findall('.//edm:Schema', namespaces):
        ns = schema_el.get('Namespace', '')
        for et in schema_el.findall('edm:EntityType', namespaces):
            index[id(et)] = (schema_el, ns)

    def extract(prop_el, entity_type_el):
        schema_el, schema_ns = index.get(id(entity_type_el), (None, ''))
        return extract_property_semantics(
            prop_el,
            entity_type_el.get('Name', ''),
            schema_ns,
            schema_el,
            namespaces,
        )
    return extract
