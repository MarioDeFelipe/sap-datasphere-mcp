import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'SAP Datasphere to AWS Sync',
  tagline: 'Advanced metadata synchronization with incremental sync and priority-based orchestration',
  favicon: 'img/sap-datasphere-logo.svg',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://ailien.studio',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For root deployment on S3 static website
  baseUrl: '/',

  // Deployment config for ailien.studio
  organizationName: 'ailien-studio',
  projectName: 'sap-datasphere-sync',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'throw',

  // Add plugins
  plugins: [],

  // Add scripts to be loaded in the client
  scripts: [],

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl:
            'https://github.com/ailien-studio/sap-datasphere-sync/tree/main/docusaurus/',
          routeBasePath: '/', // Serve docs at the site's root
          remarkPlugins: [],
          rehypePlugins: [],
        },
        theme: {
          customCss: ['./src/css/custom.css', './src/css/doc-override.css'],
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    colorMode: {
      defaultMode: 'light',
      disableSwitch: true,
    },
    image: 'img/aws-logo.svg',
    navbar: {
      title: 'SAP Datasphere Sync',
      logo: {
        alt: 'SAP Datasphere Sync Logo',
        src: 'img/sap-datasphere-logo.svg',
      },
      items: [
        {
          href: 'http://localhost:8001',
          label: 'Live Dashboard',
          position: 'right',
        },
        {
          href: 'https://ailien.studio',
          label: 'Ailien Studio',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {
              label: 'Get Started',
              to: '/',
            },
            {
              label: 'Installation',
              to: '/installation',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'Live Dashboard',
              href: 'http://localhost:8001',
            },
            {
              label: 'SAP Datasphere',
              href: 'https://www.sap.com/products/technology-platform/datasphere.html',
            },
            {
              label: 'AWS Glue',
              href: 'https://aws.amazon.com/glue/',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Ailien Studio',
              href: 'https://ailien.studio',
            },
          ],
        },
      ],
      copyright: `© ${new Date().getFullYear()} Ailien Studio. Built for SAP Datasphere to AWS synchronization.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
