# def get_test(client, scenario_id):

#     url = f"{client.base_url}/api/v4/tests/{scenario_id}"

#     response = client.session.get(url)

#     if response.status_code == 200:
#         return response.json()

#     print(response.text)
#     return None