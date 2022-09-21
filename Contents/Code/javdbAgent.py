import urllib2
import urllib
import ssl
import re
from datetime import datetime
from lxml import html



BASE_URL = 'https://javdb.com'
SEARCH_URL = BASE_URL + '/search?q=%s'
curID = "javdb"


def getElementFromUrl(url):
    return html.fromstring(unicode(request(url)))


def request(url):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    Log('Requested URL: %s' % url)
    request = urllib2.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib2.urlopen(request, context=ctx).read()    
    return response


def elementToString(ele):
    html.tostring(ele, encoding='UTF-8')


def search(query, results, media, lang):
    
    try:
        url = str(SEARCH_URL % urllib.quote_plus(query))
        results.Append(MetadataSearchResult("I am here"))
	
        for movie in getElementFromUrl(url).xpath('//div[contains(@class,"item")]'):
            moviepath = movie.xpath('.//a')[0].get("href").replace('/', "__")
            movietitle = movie.xpath('.//a')[0].get("title")
            resultname = curID +" "+ str(movietitle)
            results.Append(MetadataSearchResult(id=curID + "|" + str(moviepath),
                                                name=resultname, score=95, lang=lang))
	
	
        results.Sort('score', descending=True)
        Log(results)
    except Exception as e:
        Log('My Custome Error: %s' % e)


def update(metadata, media, lang):
    Log(str(metadata.id))
    if curID != str(metadata.id).split("|")[0]:
        return

    query = str(metadata.id).split("|")[1].replace('__', '/', 4)
    Log('Update Query: ' + BASE_URL + str(query))
    try:
        movie = getElementFromUrl(BASE_URL + query + '?locale=zh').xpath('//section/div[@class="container"]')[0]

        # title
        metadata.title = movie.xpath('.//h2')[0].text_content().strip()

        # poster
        poster = movie.xpath('.//img[contains(@class,"video-cover")]')[0].get('src').replace('/covers', "/thumbs")
        thumbUrl = poster
        thumb = request(thumbUrl)
        posterUrl = poster
        metadata.posters[posterUrl] = Proxy.Preview(thumb)

        # actors
        actors = movie.xpath('.//a[contains(@href,"actors")]')
        if (len(actors)>0):
            metadata.roles.clear()
            for actor in actors:
                role = metadata.roles.new()
                role.name = actor.text_content().split('(')[0]
                metadata.collections.add(role.name)
                actorpage = BASE_URL + actor.get("href")
                avatar = getElementFromUrl(BASE_URL + str(actor.get("href"))).xpath('//span[@class="avatar"]')
                if len(avatar)>0 :
                    role.photo = avatar[0].get('style').split("url(")[1].replace(")","")
                
        # release date & year
        moviedate = movie.xpath('.//div[@class="panel-block"]/span')[0].text_content()
        metadata.originally_available_at = datetime.strptime(
            moviedate, '%Y-%m-%d')
        metadata.year = metadata.originally_available_at.year

        # studio
        studio = movie.xpath('.//div[@class="panel-block"]')[3].xpath('.//a')[0].text_content()
        metadata.studio = studio

        # genres
        genres = movie.xpath('.//div[@class="panel-block"]')[6].xpath('.//a')
        if len(genres) > 0:
            metadata.genres.clear()
            for genreLine in genres:
                metadata.genres.add(genreLine.text_content().strip())

        """
        for info in movie.xpath('//div[contains(@class,"panel-block")]'):
		    Log(info.text_content().strip())
		    if re.search('演員',info.text_content().strip()):
			    actors = info
			    Log('matched actor')
			    metadata.roles.clear()
			    for actor in actors.xpath('//a'):
				    Log(actor.text)
				    role = metadata.roles.new()
				    role.name = actor.text_content()
                    #actorpage = BASE_URL + actor.get("href")
                    #avatar = getElementFromUrl(BASE_URL + str(actor.get("href"))).xpath('//span[@class="avatar"]')
                    #if len(avatar)>0 :
                    #    role.photo = avatar[0].get('style').split("url(")[1].replace(")","")
                    #metadata.collections.add(role.name)
            #Log('Actor: %s' % role.name)
        emptyrole = metadata.roles.new()
        emptyrole.name = "唔知住"
        
        # release date & year
        moviedate = movie.xpath('.//div[@class="panel-block"]')[0].xpath('.//span')[0].text_content()
        metadata.originally_available_at = datetime.strptime(
            moviedate, '%Y-%m-%d')
        metadata.year = metadata.originally_available_at.year
        Log('Found Date: %s' % metadata.originally_available_at)

        # studio
        studio = movie.xpath('.//div[@class="panel-block"]')[4].xpath('.//a')[0].text_content()
        Log('Studio Found: %s' % studio)
        metadata.studio = studio

        # genres
        genres = movie.xpath('.//div[@class="panel-block"]')[6].xpath('.//a')
        if len(genres) > 0:
            metadata.genres.clear()
            for genreLine in genres:
                metadata.genres.add(genreLine.text_content().strip())
        Log("ok %s" % genres)
        """
    except Exception as e:
        Log(e)
