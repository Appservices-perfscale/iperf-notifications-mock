def it_user_service():
    """
    Testing emails notifications submission
    """ 

    json_format_it_service =  [
        {
            "id": "df645b37-3e88-4fd9-a0d3-df8cc84c5216",
            "authentications": [
            {
                "principal": "rhn-engineering-lrios",
                "providerName": "rhn-engineering-lrios"
            },
            {
                "principal": "rhn-engineering-lrios",
                "providerName": "rhn-engineering-lrios"
            }
            ],
            "accountRelationships": [
            {
                "accountId": "someId",
                "startDate": "2023-01-01",
                "id":"7b92c949-5033-428c-9fe9-62f11ff0dd4f",
                "isPrimary": True,
                "permissions": [
                {
                    "permissionCode": "admin:org:all",
                    "startDate": "2023-01-01",
                    "id": "f2138fc6-f67f-4954-931e-39e5880882d2"
                }
                ],
                "emails": [
                {
                    "address": "lrios@redhat.com",
                    "isPrimary": True,
                    "id": "5b3b4c54-7bcc-45dc-adff-e99ccbc3ad54",
                    "isConfirmed": True,
                    "status": "active"
                }
                ]
            }
            ],
            "personalInformation": {
            "firstName": "foo",
            "lastNames": "faa",
            "prefix": "he",
            "localeCode": "23",
            "timeZone": "here",
            "rawOffset": "25"
            }
        }
    ]
    
    
    print("Mocking IT service")
    return json_format_it_service


print(it_user_service())