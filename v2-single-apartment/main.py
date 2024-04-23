from apartment_finder import AparmentFinder
from nexo_finder import NexoFinder


def main():
    finder: AparmentFinder = NexoFinder()
    data = finder.get_all()

    print(data)


if __name__ == "__main__":
    main()
