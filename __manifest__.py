{
    "name":"Empty Module",
    "author":"Ahmed Hamed",
    "website":"www.empty_module.com",
    "summary":"Empty Module App",
    "description":""" Empty Module App """,
    "category":"Services",
    "version":"17.1",
    "depends":[
        "base","mail",
    ],
    "data":[
        "security/ir_model_access.xml",
        "security/ir.model.access.csv",
        "views/server_action.xml",
        "reports/reports_action.xml",
        "data/sequence.xml",
        "views/menu.xml",
        "views/contract_view.xml",
    ],
    "assets":{
        "web.assets_backend":[
            "empty_module/static/src/css/style.css",
            "empty_module/static/src/css/reports.css",
        ]
    },
    "installable":True,
    "application":True
}