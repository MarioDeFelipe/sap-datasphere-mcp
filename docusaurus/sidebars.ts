import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  mainSidebar: [
    {
      type: 'category',
      label: 'Get Started',
      collapsed: false,
      items: ['intro', 'installation'],
    },
    {
      type: 'category',
      label: 'SAP Datasphere Sync',
      collapsed: false,
      items: [
        'sap-datasphere-sync/intro',
        {
          type: 'category',
          label: 'Getting Started',
          items: [
            'sap-datasphere-sync/getting-started/installation',
            'sap-datasphere-sync/getting-started/configuration',
            'sap-datasphere-sync/getting-started/quick-start',
          ],
        },
        {
          type: 'category',
          label: 'Architecture',
          items: [
            'sap-datasphere-sync/architecture/overview',
            'sap-datasphere-sync/architecture/incremental-sync',
          ],
        },
      ],
    },
  ],
};

export default sidebars;
