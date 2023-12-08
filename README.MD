# LinkedData-ResearchExplorer

An interactive platform showcasing the power of Linked Open Data in navigating and visualizing academic research insights.
Overview

LinkedData-ResearchExplorer is a web-based application that demonstrates the principles and capabilities of Linked Open Data (LOD) in the context of academic research. Utilizing data from sources like Wikidata and DBpedia, it provides a dynamic interface for exploring and analyzing scholarly papers, focusing on the field of medical ontology. The project exemplifies how LOD can be leveraged to gain insights into research trends, top authors, and their affiliations based on citation data.
## Features

Dynamic Data Fetching: Automatically pulls data from LOD sources like Wikidata and DBpedia.
Research Paper Analysis: Displays scholarly articles categorized by publication dates (day, month, year).
Author Insights: Lists top authors in the field of medical ontology, along with their academic affiliations and citation counts.
Interactive Interface: Easy-to-navigate web interface for seamless data exploration.

## Technologies

Flask: A lightweight WSGI web application framework in Python.
SPARQL: Used for querying RDF (Resource Description Framework) data from LOD sources.
HTML/CSS: For structuring and styling the web interface.

## Setup and Installation

Clone the Repository

    git clone https://github.com/outerLeitmotiv/LinkedData-ResearchExplorer.git

## Install Dependencies

Navigate to the project directory and install the required Python packages:

    pip install -r requirements.txt

## Run the Application

Start the Flask server:

    python app.py

Access the application via http://localhost:5000 in your web browser.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
## Acknowledgements

This project utilizes data from Wikidata and DBpedia.
