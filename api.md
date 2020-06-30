
 #### request body
```json
{
    "data":[
        {
            "tb_name":"simplelib",
            "max_version":0
        },
        {
            "tb_name":"bombinfo",
            "max_version":0
        },
        {
            "tb_name":"tablecategory",
            "max_version":0
        },
        {
            "tb_name":"ralationtable",
            "max_version":0
        },
        {
            "tb_name":"checklist",
            "max_version":0
        }
    ]
}
```

#### respond body
```json
{
    "ver": [
        {
            "tb_name": "simplelib",
            "max_version": "1"
        },
        {
            "tb_name": "bombinfo",
            "max_version": "1"
        },
        {
            "tb_name": "tablecategory",
            "max_version": "1"
        },
        {
            "tb_name": "relationtable",
            "max_version": "1"
        },
        {
            "tb_name": "checklist",
            "max_version": "1"
        }
    ],
    "data": {
        "simplelib":[
            {
                "id": 0,
                "type": 0,
                "zhname": "",
                "linkable": 0,
                "nickname": "",
                "cas": "",
                "formula": "",
                "formula_weight": "",
                "oxygen_balance": "",
                "nitrogen": "",
                "relative_density": "",
                "melting_point": "",
                "boiling_point": "",
                ...
            }
        ],
        "bombinfo":[
            {
                ...
            }
        ],
        "tablecategory":[
            {
                ...
            }
        ],
        "relationtable":[
            {
                ...
            }
        ],
        "checklist":[
            {
                ...
            }
        ]
    }
}

```