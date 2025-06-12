import os
from pathlib import Path

import mistapi


def create_env_file() -> None:
    """Create the environment file with Mist API credentials"""
    env_file = os.path.expanduser("~/.mist_env_ld_ro")

    print("\nMist API Configuration")
    print("======================")
    print("Available Mist hosts:")
    print("- api.mist.com (Global-01)")
    print("- api.eu.mist.com (EU-01)")
    print("- api.ac2.mist.com (Global-02)")
    print("- api.eu2.mist.com (EU-02)")
    print("- api.ac5.mist.com (APAC-01)")
    print("- api.gc7.mist.com (APAC-03)")

    host = input("\nEnter Mist host (default: api.mist.com): ") or "api.mist.com"
    api_token = input("Enter your API token: ")

    env_content = f"""host={host}
apitoken={api_token}"""

    Path(env_file).write_text(env_content)
    print(f"\nEnvironment file created at {env_file}")


def test_connection() -> None:
    """Test the API connection"""
    try:
        session = mistapi.APISession(env_file="~/.mist_env")
        session.login()
        print("\nSuccessfully connected to Mist API!")

        # List available environments
        envs = mistapi.api.v1.sites.sites.listEnvironments(session)
        print("\nAvailable environments:")
        for env in envs.data:
            print(
                f"- {env.get('description', 'Unknown')} ({env.get('url', 'Unknown URL')})"
            )

    except Exception as e:
        print(f"\nError connecting to Mist API: {e}")


if __name__ == "__main__":
    create_env_file()
    test_connection()
