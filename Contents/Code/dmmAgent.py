import urllib
import urllib2
import ssl
import re
from datetime import datetime
from lxml import html


SEARCH_URL = 'https://www.dmm.co.jp/search/=/searchstr=%s'
curID = "DMM"


def getElementFromUrl(url):
    return html.fromstring(request(url))


def request(url):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    Log('Search Query: %s' % url)
    request = urllib2.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Log(urllib2.urlopen(request,context=ctx).read())
    return urllib2.urlopen(request, context=ctx).read()


def elementToString(ele):
    html.tostring(ele, encoding='unicode')


def search(query, results, media, lang):
    try:
        url = str(SEARCH_URL % urllib.quote(query))
        for movie in getElementFromUrl(url).xpath('//p[@class="tmb"]'):
            movieurl = movie.xpath('.//a')[0].get("href").replace('/', "__")
            moviename = movie.xpath('.//img')[0].get("alt")
            Log("URL: %s" % movieurl)
            Log("NAME: %s" % moviename)
            results.Append(MetadataSearchResult(id=curID + "|" + str(movieurl),
                                                name=str(moviename+" - DMM"), score=99, lang=lang))
        results.Sort('score', descending=True)
        Log(results)
    except Exception as e:
        Log(e)


def update(metadata, media, lang):
    if curID != str(metadata.id).split("|")[0]:
        return

    query = str(metadata.id).split("|")[1].replace('__', '/', 4)
    #if re.search('\d{4}-\d\d-\d\d$', query):
    #    query = query.replace('/ja', '')
    #Log('Update Query: %s' % str(query))
    try:
        movie = getElementFromUrl(query).xpath('//div[@class="container"]')[0]
        Log('Find Movie: %s' % html.tostring(movie, encoding='UTF-8'))

        # title
        if movie.xpath('.//h3'):
            metadata.title = movie.xpath('.//h3')[0].text_content().strip()

        # poster
        image = movie.xpath('.//a[contains(@class,"bigImage")]')[0]
        thumbUrl = 'https://images.weserv.nl/?url=' + \
            image.get('href')+'&w=375&h=536&fit=cover&a=right'
        #https://images.weserv.nl/?url=https://pixboost.com/api/2/img/http://pics.dmm.co.jp/digital/video/ssni00190/ssni00190pl.jpg/asis?&auth=MTk2NjM0MDQ3MQ__&w=375&h=536&fit=cover&a=right
        #https://images.weserv.nl/?url=https%3A%2F%2Fpixboost.com%2Fapi%2F2%2Fimg%2Fhttp%3A%2F%2Fpics.dmm.co.jp%2Fdigital%2Fvideo%2Fssni00190%2Fssni00190pl.jpg%2Fasis%3F%26auth%3DMTk2NjM0MDQ3MQ__&w=375&h=536&fit=cover&a=right
        thumb = request(thumbUrl)
        posterUrl = 'https://images.weserv.nl/?url=' + \
            image.get('href')+'&w=375&h=536&fit=cover&a=right'
        metadata.posters[posterUrl] = Proxy.Preview(thumb)

        # actors
        metadata.roles.clear()
        for actor in movie.xpath('.//a[@class="avatar-box"]'):
            img = actor.xpath('.//img')[0]
            role = metadata.roles.new()
            role.name = img.get("title")
            role.photo = img.get("src")
            metadata.collections.add(role.name)
            Log('Actor: %s' % role.name)

        # release date & year
        moviedate = movie.xpath('.//p')[1].text_content().strip().replace(
            '発売日: ', '').replace('Release Date: ', '').replace('發行日期: ', '')
        metadata.originally_available_at = datetime.strptime(
            moviedate, '%Y-%m-%d')
        metadata.year = metadata.originally_available_at.year
        Log('Found Date: %s' % metadata.originally_available_at)

        # studio
        studio = movie.xpath(
            './/p')[4].text_content().strip().replace('メーカー: ', '')
        Log('Studio Found: %s' % studio)
        metadata.studio = studio

        # genres
        genres = movie.xpath('.//span[@class="genre"]')
        if len(genres) > 0:
            metadata.genres.clear()
            for genreLine in genres:
                metadata.genres.add(genreLine.text_content().strip())
        Log("ok %s" % genres)

    except Exception as e:
        Log(e)
 