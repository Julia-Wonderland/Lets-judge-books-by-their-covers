from data_load import load_and_filter
from scrapper import scrape_images


def main():
    df = load_and_filter(sample_size=2000)
    scrape_images(df)


if __name__ == "__main__":
    main()