---
id: licensing
title: Licensing Information
sidebar_label: Licensing
---

# Praximous Licensing

Praximous utilizes a licensing system to offer different sets of features tailored to various user needs, from individual developers and small teams to large enterprises. This guide explains how licensing works and how to manage your Praximous license.

## Overview

Praximous is designed with a tiered licensing model. This means that certain advanced features and capabilities may only be available with specific license tiers (e.g., Pro, Enterprise). The core functionality of Praximous is available to all users, ensuring a powerful on-premise AI orchestration experience even with the community/base version.

## License Tiers

While specific features per tier may evolve, Praximous generally offers:

*   **Community Edition**: Provides the core Praximous gateway, skill execution, provider management, and basic analytics. This is often the default functionality if no specific license key is provided or if a premium license expires.
*   **Pro Tier**: Unlocks additional features suitable for professional users and teams, potentially including more advanced skills, enhanced analytics, or higher usage limits (if applicable).
*   **Enterprise Tier**: Offers the full suite of Praximous capabilities, including premium features like advanced RAG (Retrieval-Augmented Generation) interfaces, PII (Personally Identifiable Information) redaction skills, Role-Based Access Control (RBAC), and enterprise authentication integrations (SSO/LDAP).

Please refer to our main website or contact our sales team for the most up-to-date information on features included in each tier.

## Applying Your License Key

To activate a Pro or Enterprise tier, or to ensure your Praximous instance is correctly licensed, you need to apply a license key.

1.  **Obtain Your License Key**:
    *   License keys for Pro and Enterprise tiers are typically provided upon purchase or through an agreement with Praximous.
    *   If you are evaluating a premium tier, you might receive a trial key.

2.  **Set the Environment Variable**:
    The license key is applied by setting the `PRAXIMOUS_LICENSE_KEY` environment variable in your `.env` file (located in the root of your Praximous project).

    Add the following line to your `.env` file, replacing `YOUR_LICENSE_KEY_HERE` with your actual key:

    ```env
    # .env
    PRAXIMOUS_LICENSE_KEY="YOUR_LICENSE_KEY_HERE"
    ```

3.  **Restart Praximous**:
    After setting the environment variable, you'll need to restart your Praximous instance for the changes to take effect. If you are running Praximous with Docker Compose, you can do this with:
    ```bash
    docker-compose down
    docker-compose up -d
    ```

## License Verification

Upon startup, Praximous will:

*   **Validate the License Key**: It checks the cryptographic signature of the key to ensure its authenticity.
*   **Check Expiry**: If the license has an expiration date, Praximous verifies that it is still within its validity period.
*   **Determine Tier**: The license key contains information about the tier it unlocks (e.g., Pro, Enterprise).

### Invalid or Expired Licenses

*   **Invalid Key**: If an invalid or tampered license key is detected, Praximous may refuse to start or will operate in a "Hard Stop" mode, preventing access to all functionalities.
*   **Expired Key**: If a Pro or Enterprise license key expires, Praximous will typically revert to "Degraded Functionality" mode. This usually means it will operate with the feature set of the Community Edition. You will need to obtain a new, valid license key to restore premium features.

## Feature Flagging

Praximous uses a feature flagging mechanism tied to the license tier. This means that the application code itself contains all features, but they are selectively enabled or disabled based on the validated license key. This allows for seamless upgrades and ensures that users only access the functionalities they are entitled to.

## Further Information

For detailed information on purchasing licenses, specific features included in each tier, or any licensing-related queries, please:

*   Visit our official website (link to be provided here, e.g., your main product page).
*   Contact our sales or support team.

We appreciate your support in using Praximous!

This content provides a good starting point. You'll want to replace placeholders like "(link to be provided here, e.g., your main product page)" with actual links once your website is more complete.

After saving this, restart your Docusaurus server and check out the new licensing guide!
