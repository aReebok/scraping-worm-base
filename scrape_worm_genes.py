# WRITTEN B UNKNWON SOURCE -- doesn't work as of now
# Scrapes all the worm genes and places them in a csv file
# that can be opened in a spreadsheet like Excel.
#
# Usage: 'python scrape_worm_genes.py [input_file_name]'
#
# The input file should have a new gene sequence in each
# line.
#
# This script requires python and the lxml library.
#

import json, lxml, lxml.html, sys, urllib

def open_gene_page(gene_name):
  '''
  Given a gene name, returns the tree for its web page.
  '''
  url = "http://www.wormbase.org/search/gene/" + gene_name
  page = lxml.html.fromstring(url)
  return page

def open_sub_gene_page(gene_key, sub_heading):
  '''
  Opens a subpage.
  '''
  url = "http://www.wormbase.org/rest/widget/gene/"
  url += gene_key + "/" + sub_heading
  return lxml.html.fromstring(url)

def write_row_to_file(row, output_file):
  '''
  Takes a row as a list and writes it to the output file.
  '''
  for i in xrange(0, len(row)):
    row[i] = row[i].replace('\t', ' ')
    row[i] = row[i].replace('\n', ' ')
    row[i] = row[i].replace('\r', ' ')
  output_file.write('\t'.join(row) + '\n')

if __name__ == '__main__':
  # Test for proper usage.
  if len(sys.argv) != 2:
    print 'Error: Proper usage is \'python scrape_worm_genes.py [input_file_name]\''

  # Open data file. The data should have a new sequence on each line.
  input_file = open(sys.argv[1], 'r')

  # Open new csv.
  output_file = open('data.tsv', 'w+')
  
  # Write headers.
  row = ['Sequence', 'Gene', 'Overview', 'Homology - Human', 'Homology - Fly', 'Homology - Yeast', 'Ontology']
  write_row_to_file(row, output_file)

  for sequence in input_file:
    # If input blank, continue.
    sequence = sequence.strip()
    if not sequence:
      continue

    # Get the page.
    page = open_gene_page(sequence)

    # Create data row.
    row = [sequence, ]

    # Is gene found?
    exists = page.xpath("//*[@id='widget-gene']")
    if not exists:
      write_row_to_file(row, output_file)
      continue

    # Get gene.
    gene = page.xpath("//title")
    gene = gene[0].text.strip().split(' ')[0]
    row.append(gene)

    # Get gene key.
    header = page.xpath('//*[@id="header"]')
    gene_json = json.loads(header[0].get('data-page'))
    gene_key = gene_json["wbid"]

    # Gets the overview.
    overview_page = open_sub_gene_page(gene_key, 'overview')
    description = overview_page.xpath("//*[@class='evidence  result']")
    if not description:
      description = overview_page.xpath("//*[@class='description']")
    description = description[0].text_content()
    row.append(description)

    # Gets the homology.
    homology_page = open_sub_gene_page(gene_key, 'homology')
    homology = homology_page.xpath("//*[@id='table_best_blastp_matches_by']//td[contains(span, 'sapiens')]")
    if homology:
      homology = homology[0].getnext().getnext().text_content()
    else:
      homology = ''
    row.append(homology)

    # Gets the fly homology.
    homology = homology_page.xpath("//*[@id='table_best_blastp_matches_by']//td[contains(span, 'melanogaster')]")
    if homology:
      homology = homology[0].getnext().getnext().text_content()
    else:
      homology = ''
    row.append(homology)

    # Gets the yeast homology.
    homology = homology_page.xpath("//*[@id='table_best_blastp_matches_by']//td[contains(span, 'cerevisiae')]")
    if homology:
      homology = homology[0].getnext().getnext().text_content()
    else:
      homology = ''
    row.append(homology)

    # Gets the ontology.
    ontology_page = open_sub_gene_page(gene_key, 'gene_ontology')
    ontology = ontology_page.xpath("//div[@class='field-title' and contains(span, 'Molecular function')]")
    exists = True
    if ontology:
      ontology = ontology_page.xpath("//tbody")
      if ontology:
        ontology = ontology[-1]
        ontology = ontology.getchildren()
        seen = []
        for r in ontology:
          tds = r.getchildren()
          content = tds[0].text_content()
          if content not in seen:
            seen.append(content)
        ontology = ', '.join(seen)
      else:
        exists = False
    else:
      ontology = ''
    if not exists:
      ontology = ''
    row.append(ontology)

    write_row_to_file(row, output_file)
    print 'Gene ' + gene + ' written to file.'

