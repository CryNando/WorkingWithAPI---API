# -*- coding: utf-8 -*-

#author - Luis Fernando
"""Descrição
Um jogador de jogos Online deseja obter algumas informações estatísticas e instrutivas sobre alguns Jogos. 
Com esse Script ele é capaz de obter informações sobre o jogo League of Legends e Jogos da Steam
Caso ele opte por League of Legends, ele informa seu nick e com isso retornamos informações sobre suas últimas 20 partidas, dentre essas informações possue Lane/Campeão/Número de Abates/Assistências e mortes. 
Caso ele opte pela Steam, ele informa seu URL do Perfil e com isso retornamos a quantidade de jogos que ele já jogou, Nome de Cada jogo e a quantidade de horas total e nas últimas duas semanas, e por fim seu nível na Steam.
"""

import requests, sys, json, io, math
import xml.etree.ElementTree as ET

#KEYS Obtidas no Site da RIOT e Steam
keyLOL = "" #essa key expira Thu, Apr 26th, 2018 @ 9:04am (PT) !! Quando for testar entre em contato para que eu possa enviar uma nova key.
keySteam = ""

#Váriaveis de Controle
totalkills = 0
totalassists = 0
totaldeath = 0
totalfarm = 0
totalvitoria = 0
totalderrota = 0

#Compilar no sistema utilizando UTF8
reload(sys)
sys.setdefaultencoding('utf8')

#Verifica se o número de parametros está corretos. Deve ser 3, o default de execução, o jogo escolhido (Steam ou LeagueofLegends) e o UrlPerfil caso seja Steam ou Nick caso seja LOL
if not (len(sys.argv) == 3):
	print "Número de parametros errado. Consulte o README!"
	sys.exit()
else:
	#verifica a opção escolhida pelo usuário
	if (sys.argv[1] == "LeagueofLegends"):

		nickname = sys.argv[2]
		#API que retorna informações da conta do usuário
		urlID = "https://br1.api.riotgames.com/lol/summoner/v3/summoners/by-name/" + nickname + "?api_key="+keyLOL

		response = requests.get(urlID)
		response.raise_for_status()

		resultData = json.loads(response.text)
		accountId = resultData["accountId"]

		#APi que retorna informações das últimas 20 partidas do usuário
		urlRecents = "https://br1.api.riotgames.com/lol/match/v3/matchlists/by-account/" + str(accountId) + "/recent?api_key="+keyLOL

		response = requests.get(urlRecents)
		response.raise_for_status()

		#abre arquivo que contém informações dos campeões do jogo. Arquivo foi salvo com informações de uma API também, mas por motivos de bloqueio de múltiplas requisições deixei salvo direto no arquivo.
		with io.open('champions.json', 'r', encoding='latin-1') as arqChamp:
			resultChamp = json.loads(arqChamp.read())


		resultData = json.loads(response.text)
		#percorre as respostas das requisições, pega e exibe as informações relevantes
		for x in resultData["matches"]:
			print "Você jogou no %s " % x["lane"]
			print "Você jogou de %s " % resultChamp["keys"][str(x["champion"])]
			urlMatch = "https://br1.api.riotgames.com/lol/match/v3/matches/"+ str(x["gameId"]) +"?api_key="+keyLOL
			responseMatch = requests.get(urlMatch)
			responseMatch.raise_for_status()
			resultMatch = json.loads(responseMatch.text)
			for y in range(len(resultMatch["participantIdentities"])):
				if resultMatch["participantIdentities"][y]["player"]["summonerName"] == nickname:
					participantid = resultMatch["participantIdentities"][y]["participantId"]
					break;
			for z in range(len(resultMatch["participants"])):
				if resultMatch["participants"][z]["participantId"] == participantid :
					kills = resultMatch["participants"][z]["stats"]["kills"]
					assists = resultMatch["participants"][z]["stats"]["assists"]
					death = resultMatch["participants"][z]["stats"]["deaths"]
					win_or_lose = resultMatch["participants"][z]["stats"]["win"]
					farm = resultMatch["participants"][z]["stats"]["totalMinionsKilled"]
					break;
			print "Abates %d " % kills
			totalkills = totalkills + kills
			print "Assistências %d " % assists
			totalassists = totalassists + assists
			print "Mortes %d " % death
			totaldeath = totaldeath + death
			if win_or_lose:
				print "Você Venceu!"
				totalvitoria = totalvitoria + 1
			else:
				print "Você Perdeu!"
				totalderrota = totalderrota + 1 

			print "\n ----------------------------- \n"

		print "Média de %d Abates nas últimas 20 partidas" % (totalkills/20)
		print "Média de %d Assistências nas últimas 20 partidas" % (totalassists/20)
		print "Média de %d Mortes nas últimas 20 partidas" % (totaldeath/20)
		print "Você venceu %d e perdeu %d nas últimas 20 partidas " % (totalvitoria,totalderrota)
		print "AMA Total - %d/%d/%d " % (totalkills,totaldeath,totalassists)
		print "AMA Média - %d/%d/%d " % ((totalkills/20), (totaldeath/20), (totalassists/20))

	#Caso escolha a opção Steam
	elif (sys.argv[1] == "Steam"):

		#pega o ID do usuário através da sua página de perfil
		url = sys.argv[2] + "?xml=1"
		response = requests.get(url)
		response.raise_for_status()

		getProfile = ET.fromstring(response.text)
		idSteam = getProfile.find("steamID64").text

		#Pega o nick utilizado pelo usuário através da API
		urlNick = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key=" + key + "&steamids=" + idSteam
		responseNick = requests.get(urlNick)
		responseNick.raise_for_status()
		resultNick = json.loads(responseNick.text)

		print "Olá " + resultNick["response"]["players"][0]["personaname"] + " Confira suas informações abaixo"


		urlRecents = "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/?key=" + key + "&steamid=" + idSteam

		responseRecents = requests.get(urlRecents)
		responseRecents.raise_for_status()
		resultRecents = json.loads(responseRecents.text)

		totalgames = resultRecents["response"]["total_count"]
		print "Foram encontrados %d vinculados ao seu perfil" % totalgames
		#percorre as respostas das requisições, pega e exibe as informações relevantes
		for game in resultRecents["response"]["games"]:
			name = game["name"]
			print "Jogo: " + name
			total2Sem = game["playtime_2weeks"]
			#função round para arrendondar o número para casa decimal mais próximo.
			print "Total jogado nas últimas 2 semanas: %0.2fh " % round((total2Sem/60.0),1)
			totaltotal = game["playtime_forever"]
			#função ceil para arrendonar o número sempre pra números exatos mais próximo.
			print "Total jogado: %dh " % (math.ceil(totaltotal/60))


		urlLevel = "https://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key=" + key + "&steamid=" + idSteam 
		responseLevel = requests.get(urlLevel)
		responseLevel.raise_for_status()
		resultLevel = json.loads(responseLevel.text)

		print "Você possui Level %d na Steam " % resultLevel["response"]["player_level"]

	else:
		print "Parametro inválido, consulte o README."