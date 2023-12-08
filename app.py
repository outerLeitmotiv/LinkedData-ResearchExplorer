from collections import defaultdict

from flask import Flask, render_template
from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime, timedelta

app = Flask(__name__)


def fetch_papers():
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery("""
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>

SELECT ?paperTitle ?publicationDate ?authorName ?publishedIn ?citesWork WHERE {
  ?paper wdt:P31 wd:Q13442814; # Scholarly article
         wdt:P921 wd:Q324254;  # Main subject is ontology
         wdt:P577 ?publicationDate; # Publication date
         p:P2093 ?authorStatement. # Author name string

  OPTIONAL { ?paper wdt:P1433 ?journal. # Published in
             ?journal rdfs:label ?publishedIn FILTER(LANG(?publishedIn) = "en"). }

  OPTIONAL { ?paper wdt:P2860 ?citedWork. # Cites work
             ?citedWork rdfs:label ?citesWork FILTER(LANG(?citesWork) = "en"). }

  ?authorStatement ps:P2093 ?authorName.

  OPTIONAL { ?paper rdfs:label ?title FILTER(LANG(?title) = "en"). }
  BIND(COALESCE(?title, "No title available") AS ?paperTitle)
}

    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    papers = defaultdict(lambda: {
        'publicationDate': '',
        'authors': set(),
        'publishedIn': '',
        'citesWork': set(),
        'displayed': False  # Flag to keep track if the paper has been categorized
    })
    papers_day, papers_month, papers_year = [], [], []
    current_date = datetime.now()

    for result in results["results"]["bindings"]:
        title = result['paperTitle']['value'] if 'paperTitle' in result else 'No Title'
        publication_date_str = result['publicationDate']['value'].split('T')[0] if 'publicationDate' in result else ''

        if publication_date_str:
            publication_date = datetime.strptime(publication_date_str, '%Y-%m-%d')
            delta = current_date - publication_date

            paper = papers[title]
            paper['publicationDate'] = publication_date_str
            paper['authors'].add(result['authorName']['value'] if 'authorName' in result else 'No Author')
            paper['publishedIn'] = result['publishedIn']['value'] if 'publishedIn' in result else 'No Journal'
            paper['citesWork'].add(result['citesWork']['value'] if 'citesWork' in result else 'No Citation')

            if not paper['displayed']:
                if delta.days < 1:
                    papers_day.append(title)
                elif delta.days < 30:
                    papers_month.append(title)
                elif delta.days < 365:
                    papers_year.append(title)
                paper['displayed'] = True

    for paper in papers.values():
        paper['authors'] = list(paper['authors'])
        paper['citesWork'] = list(paper['citesWork'])

    return papers, papers_day, papers_month, papers_year


def fetch_top_authors():
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery("""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        
        SELECT ?authorName ?partOfName (COUNT(DISTINCT ?citingPaper) AS ?citationCount) WHERE {
          # Select scholarly articles on medical ontology
          ?paper wdt:P31 wd:Q13442814; # Scholarly article
                 wdt:P921 wd:Q324254;  # Main subject is ontology
                 wdt:P50 ?author.       # Author of the paper
        
          # Get author names
          ?author rdfs:label ?authorName FILTER(LANG(?authorName) = "en"). 
        
          # Get the part (e.g., university or organization) the author is associated with
          OPTIONAL { 
            ?author wdt:P361 ?partOf.
            ?partOf rdfs:label ?partOfName FILTER(LANG(?partOfName) = "en").
          }
        
          # Find papers that cite these scholarly articles
          ?citingPaper wdt:P2860 ?paper.
        }
        GROUP BY ?authorName ?partOfName
        ORDER BY DESC(?citationCount)
        LIMIT 10
    """)
    sparql.setReturnFormat(JSON)
    r_authors = sparql.query().convert()

    top_authors = []
    for a_result in r_authors["results"]["bindings"]:
        author = {
            'name': a_result['authorName']['value'],
            'affiliation': a_result.get('partOfName', {}).get('value', 'Unknown'),  # Updated to handle missing data
            'citations': int(a_result['citationCount']['value'])
        }
        top_authors.append(author)

    return top_authors


@app.route('/papers')
def show_papers():
    papers_dict, papers_day, papers_month, papers_year = fetch_papers()
    top_authors = fetch_top_authors()
    return render_template('papers.html',
                           papers=papers_dict,
                           papers_day=papers_day,
                           papers_month=papers_month,
                           papers_year=papers_year,
                           top_authors=top_authors)


if __name__ == '__main__':
    app.run(debug=True)
