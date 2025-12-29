def saml_settings():
    return {
        "strict": True,
        "debug": False,

        "sp": {
            "entityId": "https://your-app.example.com/metadata",
            "assertionConsumerService": {
                "url": "https://your-app.example.com/saml/acs",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "singleLogoutService": {
                "url": "https://your-app.example.com/saml/logout",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "x509cert": "",
            "privateKey": "",
        },

        "idp": {
            "entityId": "REPLACE_WITH_AWS_IDENTITY_CENTER_ENTITY_ID",
            "singleSignOnService": {
                "url": "REPLACE_WITH_SSO_URL",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "singleLogoutService": {
                "url": "REPLACE_WITH_SLO_URL",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "x509cert": "REPLACE_WITH_IDP_CERT",
        },
    }
