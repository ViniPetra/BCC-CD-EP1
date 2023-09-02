import scrapy


class PokeSpider(scrapy.Spider):
  name = 'pokespider'
  start_urls = ['https://pokemondb.net/pokedex/all']

  def parse(self, response):
    tabela_pokedex = "table#pokedex > tbody > tr"
    linhas = response.css(tabela_pokedex)

    for linha in linhas:
      coluna_href = linha.css("td:nth-child(2) > a::attr(href)")
      yield response.follow(coluna_href.get(), self.parser_pokemon)

  def parser_pokemon(self, response):
    nome = response.css("#main > h1:nth-child(1)::text").get()
    numero = response.css(
      "table.vitals-table > tbody > tr:nth-child(1) > td:nth-child(2) > strong:nth-child(1)::text"
    ).get()
    altura = response.css(
      "table.vitals-table > tbody > tr:nth-child(4) > td:nth-child(2)::text"
    ).get()
    peso = response.css(
      "table.vitals-table > tbody > tr:nth-child(5) > td:nth-child(2)::text"
    ).get()
    tipo = response.css(
      "table.vitals-table > tbody > tr:nth-child(2) > td:nth-child(2)>  a:nth-child(1)::text"
    ).get()
    tipo2 = response.css(
      "table.vitals-table > tbody > tr:nth-child(2) > td:nth-child(2)>  a:nth-child(2)::text"
    ).get()

    evolucoes = []
    tabela_evolucoes = response.css("div.infocard")

    for card in tabela_evolucoes:
      e_num = card.css("small::text").get()
      e_nome = card.css("a.ent-name::text").get()
      e_url = card.css("a.ent-name::attr(href)").get()

      evolucao = {
        'numero_evolucao': e_num,
        'nome_evolucao': e_nome,
        'url_evolucao': e_url
      }
      evolucoes.append(evolucao)

    link_habilidades = response.css(
      'table.vitals-table > tbody > tr:nth-child(6) > td:nth-child(2) > span:nth-child(1) > a:nth-child(1)::attr(href)'
    ).get()

    yield response.follow(link_habilidades,
                          self.parse_habilidade,
                          meta={'habilidades': []},
                          cb_kwargs={
                            'nome': nome,
                            'numero': numero,
                            'peso': peso,
                            'altura': altura,
                            'tipo': tipo,
                            'tipo_2': tipo2,
                            'evolucoes': evolucoes
                          })

  def parse_habilidade(self, response, nome, numero, peso, altura, tipo,
                       tipo_2, evolucoes):
    habilidades_info = {
      'nome':
      response.css(
        "html body main#main.main-content.grid-container h1::text").get(),
      'descricao':
      response.css("div.grid-col:nth-child(1) > p:nth-child(2)::text").get(),
      'url_habilidade':
      response.url
    }

    habilidades = response.meta['habilidades']
    habilidades.append(habilidades_info)

    yield {
      'nome': nome,
      'numero': numero,
      'peso': peso,
      'altura': altura,
      'tipo': tipo,
      'tipo_2': tipo_2,
      'evolucoes': evolucoes,
      'habilidades': habilidades
    }
