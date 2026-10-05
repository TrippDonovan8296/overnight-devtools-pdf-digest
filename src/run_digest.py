from src.digest_service import DevtoolsRecord, client_from_env, render_digest


def main() -> None:
    records = [
        DevtoolsRecord("build", "nightly compiler", "42 packages built"),
        DevtoolsRecord("release", "mobile 2.4.0", "published to the release channel"),
        DevtoolsRecord("diagnostic", "slow test suite", "integration tests exceeded ten minutes"),
    ]
    result = render_digest(records, client_from_env())
    print(result["summary"])
    print("PDF result:", result["pdf"])


if __name__ == "__main__":
    main()
