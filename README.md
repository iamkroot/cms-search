# CMS Search Engine

Search engine built to enable users to query the various Word and Powerpoint files that are uploaded to the Moodle CMS of BITS Pilani Hyderabad.

## Features
* Search through the various file contents of the documents on the CMS
* Returns the closest matching documents to the query
* For each document, you are shown the 5 most similar sentences containing your query words
* The index of documents is updated regularly and dynamically - no need to reconstruct it everytime
* Backend in MongoDB for persisting the index

## How to run
1. Clone this repo / click "Download as Zip" and extract the files.
2. Rename the `sample_config.toml` to `config.toml` and set the required values.
3. Ensure Python 3.7 is installed, and in your system `PATH`.
4. Install pipenv using `pip install -U pipenv`.
5. In the project folder, run `pipenv install` to install all python dependencies.
6. Download the nltk datasets:
	1. Run `pipenv run python`.
	2. `>>> nltk.download("stopwords")`.
	3. `>>> nltk.download("wordnet")`.
	4. `>>> nltk.download("genesis")`.

To generate the index: `pipenv run python indexer.py`. It will go through all the enrolled courses in your CMS account, and if a new file is encountered, add it to the index after processing it.

To query the index: `pipenv run python main.py`.
