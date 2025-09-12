class TestReferralGenerateLink:
    async def test_generate_project_not_valid(self, auth_ac, query_counter):
        response = await auth_ac.client.get(
            "/app/v1/referral/generate_link?" "ref_type=project" "&fund_id=1", cookies=auth_ac.cookies.dict()
        )
        assert response.status_code == 422

    async def test_generate_project_200(self, auth_ac, query_counter):
        response = await auth_ac.client.get(
            "/app/v1/referral/generate_link?" "ref_type=project" "&project_id=1", cookies=auth_ac.cookies.dict()
        )
        assert response.status_code == 200
        assert "/v1/projects/detail/1?ref=" in response.json()
