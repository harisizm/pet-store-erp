{
    'name': 'Hisabkar Privacy',
    'summary': 'Zero egress: nothing leaves to the platform vendor or to unlisted third parties',
    'description': """
Implements ADR-0005 / NFR-SEC-005..007:

* removes the vendor's paid-service (IAP) module family and refuses to install it again;
* neutralises the weekly usage report (publisher warranty);
* disables Gravatar lookups and link previews;
* guards every outbound connection against an allowlist;
* sends a Content-Security-Policy that keeps the browser on our own origin.
""",
    'version': '18.0.1.0.0',
    'category': 'Hidden',
    'license': 'Other proprietary',
    'author': 'Hisabkar',
    # html_editor: its link-preview routes are overridden (mail already depends on it).
    'depends': ['base', 'web', 'mail', 'html_editor'],
    'data': [
        'data/hisabkar_privacy_data.xml',
    ],
    # Recorded exception to the "auto_install only for glue modules" convention (ADR-0005): the
    # module must be on every database. Auto-install covers databases created after it is on the
    # addons path; installers and setup scripts also install it explicitly, because auto-install
    # does not fire on a database whose dependencies were installed earlier.
    'auto_install': True,
    'installable': True,
}
