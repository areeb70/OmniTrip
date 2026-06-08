from matchdayops.tracing import configure_tracing, flush_tracing, traced


@traced("phoenix.connection_test")
def hello_phoenix() -> str:
    return "Phoenix test trace sent from MatchDayOps."


def main() -> None:
    configure_tracing()
    print(hello_phoenix())
    flush_tracing()
    print("Now refresh Phoenix and open your project. Total Traces should increase.")


if __name__ == "__main__":
    main()
