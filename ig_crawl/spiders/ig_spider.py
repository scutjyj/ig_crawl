# coding=utf-8

import time
import json
import re
import urllib2
from hashlib import md5
import traceback
import scrapy
import urllib3


class InstagramSpider(scrapy.Spider):
    name = "ig"
    username = "celinedion"
    base_url = "https://www.instagram.com"
    start_urls = [
        "{base_url}/{username}/".format(base_url=base_url, username=username)
    ]

    def parse(self, response):
        try:
            share_data_str = re.findall(r'window._sharedData = (.*?);</script>', response.text)[0]
            share_data = json.loads(share_data_str)
            self.rhx_gis = share_data.get('rhx_gis')
            user_info_all = share_data['entry_data']['ProfilePage'][0]['graphql']['user']
            user_id = user_info_all.get('id')
            username = user_info_all.get('username')
            followers = user_info_all.get('edge_followed_by').get('count')
            followings = user_info_all.get('edge_follow').get('count')
            post_counts = user_info_all['edge_owner_to_timeline_media']['count']
            posts_info_list = user_info_all['edge_owner_to_timeline_media']['edges']
            pagination_info = user_info_all['edge_owner_to_timeline_media']['page_info']
            has_next_page = pagination_info.get('has_next_page')
            if has_next_page:
                end_cursor = pagination_info.get('end_cursor')
            js_file_rel_path = re.findall(r'src=.*?ProfilePageContainer\.js.*?"',
                                          response.text)[0].split('=')[1].strip('"')
            # the urllib3 needs some config to request the https page.
            #js_text = urllib3.PoolManager().request('GET', self.base_url+js_file_rel_path).data
            js_text = urllib2.urlopen(self.base_url+js_file_rel_path).read()
            query_id = re.findall(r'profilePosts\.byUserId.*?queryId:"(.*?)"', js_text)[0]
            # debugging code.
            print("rhx_gis={0}".format(self.rhx_gis))
            print("username={0}".format(username))
            print("followers={0}".format(followers))
            print("pagination_info={0}".format(pagination_info))
            print("query_id={0}".format(query_id))
            # parse and extract the posts contents.
            for node in posts_info_list:
                for k, v in node.get('node').iteritems():
                    #print k, '=', v
                    pass
            variables = '{"id":"%s","first":12,"after":"%s"}' % (user_id, end_cursor)
            next_page_url = self.base_url+'/graphql/query/?query_hash=%s&variables=%s' % (query_id,
                                                                                          urllib2.quote(variables))
            print "next_page_url=", next_page_url
            headers = {
                "x-ig-app-id": str(936619743392459)
            }
            x_instagram_gis_seeds = self.rhx_gis + ':' + variables
            x_instagram_gis = md5(x_instagram_gis_seeds).hexdigest()
            print "x_instagram_gis_seeds=", x_instagram_gis_seeds
            print "x_instagram_gis=", x_instagram_gis
            headers['x-instagram-gis'] = x_instagram_gis
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                         'Chrome/72.0.3626.121 Safari/537.36'
            headers['user-agent'] = user_agent
            print 'headers=', headers
            time.sleep(3)
            yield scrapy.Request(next_page_url, headers=headers, callback=self.parse_next_page)
        except Exception as e:
            #raise e
            traceback.print_exc()

    def parse_next_page(self, response):
        print "response.status=", response.status
        print "response.text=", response.text



