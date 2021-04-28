import requests
import re
from pyquery import PyQuery
from bs4 import BeautifulSoup
from urllib import parse
import pandas as pd
import time
import datetime
import os
from queue import Queue

# 增加重试连接次数
requests.DEFAULT_RETRIES = 5


file_name = r'D:\A-HZX\招标信息表.xlsx'

""" 招标信息获取 """

headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
}
zs = {
	'水乡新城片区': 0
}

# 延时时间（秒）
delayed = 0.1

fs = {
	'中堂镇': 'http://www.dg.gov.cn/zhongtang/gczb/index.html',
	'望牛墩镇': 'http://www.wndcj.com/portal/list/index/id/1.html',
	'万江街道': 'http://www.dg.gov.cn/wanjiang/zt/zbxmgb/jsgcxmxx/',
	'中山市': 'https://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?node=58',
	'漳州市': 'http://www.zzgcjyzx.com/Front/gcxx/002001/002001001/',
}

fs_xs = {

	'横沥镇': 'http://www.dg.gov.cn/dghlz/gkmlpt/api/all/2972?page=1',  # 'http://www.dg.gov.cn/dghlz/gkmlpt/index#2972',  # 横沥
	'石排镇': 'http://www.dg.gov.cn/dgspz/gkmlpt/api/all/3127?page=1',  # 'http://www.dg.gov.cn/dgspz/gkmlpt/index#3127',  # 石排
	'大岭山镇': 'http://www.dg.gov.cn/dgdlsz/gkmlpt/api/all/2449?page=1',  # 大岭山
	'南城街道': 'http://www.dg.gov.cn/dgncjd/gkmlpt/api/all/1866?page=1',  # 南城
	'石碣镇': 'http://www.dg.gov.cn/dgszz/gkmlpt/api/all/2068?page=1',  # 石碣
	'桥头镇': 'http://www.dg.gov.cn/dgqtz/gkmlpt/api/all/2930?page=1',  #  # 桥头镇
	'茶山镇': 'http://www.dg.gov.cn/dgcsz/gkmlpt/api/all/3177?page=1',
	'黄江镇': 'http://www.dg.gov.cn/dghjz/gkmlpt/api/all/3579?page=1',
	'谢岗镇': 'http://www.dg.gov.cn/dgxgz/gkmlpt/api/all/3659?page=1',
	'樟木头镇': 'http://www.dg.gov.cn/dgzmtz/gkmlpt/api/all/2630?page=1',
	'常平镇': 'http://www.dg.gov.cn/dgcpz/gkmlpt/api/all/3489?page=1',
	'东坑镇': 'http://www.dg.gov.cn/dgdkz/gkmlpt/api/all/3034?page=1',
	'道滘镇': 'http://www.dg.gov.cn/dgdjz/gkmlpt/api/all/2205?page=1',
	'高埗镇': 'http://www.dg.gov.cn/dggbz/gkmlpt/api/all/2119?page=1',
	'莞城街道': 'http://www.dg.gov.cn/dgzcjd/gkmlpt/api/all/1637?page=1',
	'东城街道': 'http://www.dg.gov.cn/dgdcjd/gkmlpt/api/all/1781?page=1',
	'企石镇': 'http://www.dg.gov.cn/dgqsz/gkmlpt/api/all/3083?page=1',
	'寮步镇': 'http://www.dg.gov.cn/dgzbz/gkmlpt/api/all/2402?page=1',
	'大朗镇': 'http://www.dg.gov.cn/dgdlz/gkmlpt/api/all/2533?page=1',
	'长安镇': 'http://www.dg.gov.cn/dgcaz/gkmlpt/api/all/2351?page=1',
	'沙田镇': 'http://www.dg.gov.cn/dgstz/gkmlpt/api/all/2301?page=1',
	'凤岗镇': 'http://www.dg.gov.cn/dgfgz/gkmlpt/api/all/2680?page=1',
	'红梅镇': 'http://www.dg.gov.cn/dghmz/gkmlpt/api/all/2163?page=1',

	'麻涌镇': 'http://www.dg.gov.cn/postmeta/i/8665.json',
	'塘厦镇': 'http://www.dg.gov.cn/postmeta/i/18120.json',
	'滨海湾新区': 'http://bhwxq.dg.gov.cn/postmeta/i/278.json',
	'厚街镇': 'http://www.dg.gov.cn/postmeta/i/9149.json',
	'清溪镇': 'http://www.dg.gov.cn/postmeta/i/10143.json',

}


LS_url = set()  # 已经获取过招标数据的URL


def get_file_new(file_name):
	""" 获取最新的文件 """
	fold = os.path.dirname(file_name)
	files = [os.path.join(fold,i) for i in os.listdir(fold) if i[:5]=='招标信息表']
	# files = [(os.path.getctime(i), i) for i in files]
	files = [(os.path.getmtime(i), i) for i in files]
	files.sort(key=lambda x: x[0])
	return files[-1][-1]


def get_burl(url):
	""" 原始URL """
	v = parse.urlparse(url)
	burl = v.scheme + '://' + v.netloc
	return burl


def get_tzzz(data2):
	""" 获取投资资质 """
	if isinstance(data2, PyQuery):
		compiles = ("p:contains('本次招标要求投标人具备')", "p:contains('投标人资质等级要求')", "tr:contains('资质要求')",
					"p:contains('投标单位资质等级要求')")   #
		for c in compiles:
			jg = data2(c)
			if jg:
				jg = jg[0].text_content()
				jg = jg.split('，')[-1] if jg else ''
				jg2 = re.findall('[^\x00-\xff]+', jg)
				if jg2:
					return '，'.join(jg2)
				return jg
	else:
		compiles = ('投标人必须具备(.*?)级', '要求投标人具备有效的(.*?)级')
		for c in compiles:
			jg = re.findall(c, data2)
			if jg:
				jg2 = re.findall('[^\x00-\xff]+', jg[0])
				if jg2:
					return jg2[0]

				return jg[0]
	return ''


def get_tzje(data2):
	""" 获取金额 """
	if isinstance(data2, PyQuery):
		compiles = ("p:contains('金额')", "span:contains('人民币')", "p:contains('元')", "tr:contains('投资金额')")
		for c in compiles:
			jgs = data2(c)
			if jgs:
				jgs = '，'.join([str(i.text_content()) for i in jgs])
				return jgs.replace('\xa0', '')
	else:
		compiles = ('金额(.*?)元', '投资为(.*?)元', '投资额(.*?)元', )
		for c in compiles:
			jg = re.findall(c, data2)
			if jg:
				return '，'.join(jg)
	return ''

def get_zbwjs(data2):
	""" 获取招标文件 """
	if isinstance(data2, PyQuery):
		compiles = ("p:contains('凡有意参加投标者')", "p:contains('招标文件售卖地点')", "p:contains('招标文件可在')", "p:contains('获取招标文件方式')")  # ：
		for c in compiles:
			jg = data2(c)
			if jg:
				return jg[0].text_content()
	else:
		compiles = ('投标人参与投标前(.*?)。',)
		for c in compiles:
			jg = re.findall(c, data2)
			if jg:
				return '，'.join(jg)
	return ''

def get_jzsjs(data2):
	""" 获取截止时间 """
	if isinstance(data2, PyQuery):
		compiles = ("p:contains('递交的截止时间')", "p:contains('递交截止时间')", "p:contains('提交截止时间')",
					"p:contains('投标截止及开标时间')", "p:contains('递交截止时间')")  # 投标截止及开标时间
		for c in compiles:
			jg = data2(c)
			if jg:
				return jg[0].text_content()
	else:
		compiles = ()
		for c in compiles:
			jg = re.findall(c, data2)
			if jg:
				return jg[0]
	return ''

def get_zbbhs(data2):
	""" 获取招标编号 """
	if isinstance(data2, PyQuery):
		compiles = ("p:contains('招标编号')", "tr:contains('招标编号')", "p:contains('项目编号')", "p:contains('采购编号：')")  #
		for c in compiles:
			jg = data2(c)
			if jg:
				jg = jg[-1].text_content()
				jg = jg.replace('\xa0', '') if jg else ''
				return jg
	else:
		compiles = ()
		for c in compiles:
			jg = re.findall(c, data2)
			if jg:
				return jg[0]
	return ''


def get_name(data2):
	""" 获取项目名称 """
	if isinstance(data2, PyQuery):
		compiles = ("title", ".title",)
		for c in compiles:
			jg = data2(c)
			if jg:
				return jg[0].text_content()
	return ''


def get_all(zq_name):
	""" 获取相似镇区数据 """
	url = fs_xs[zq_name]
	data = requests.get(url, headers=headers).json()
	data = data['articles']
	divs = [(i['title'], i['url'], i['created_at']) for i in data if '招标公告' in i['title']]
	res = []
	for i in divs:
		try:
			if i[1] in LS_url:
				continue
			res2 = []
			url2 = i[1]  # 项目地址
			data2 = requests.get(url2, headers=headers).text
			data2 = PyQuery(data2)
			name = i[0]  # 项目名称
			res2.append(name)
			res2.append(url2)
			fbrq = i[2]  # 发布日期
			res2.append(fbrq)
			zbbh = get_zbbhs(data2)
			res2.append(zbbh)
			jes = get_tzje(data2)  # 金额（包括投资金和担保金）
			res2.append(jes)
			tzzz = get_tzzz(data2)
			res2.append(tzzz)
			zbwj = get_zbwjs(data2)  # 招标文件获取方式
			res2.append(zbwj)
			jzsj = get_jzsjs(data2)
			res2.append(jzsj)
			res2.append(zq_name)
			res.append(res2)
			time.sleep(delayed)

			# 关闭多余连接，避免连接超过网站的访问次数，被禁止访问
			s = requests.session()
			s.keep_alive = False

		except Exception as e:
			print(zq_name, e)
	return res


def get_alls():
	res_alls = []
	for zq in fs_xs:

		s = requests.session()
		s.keep_alive = False
		
		res = get_all(zq)
		res_alls += res
	return res_alls


def get_zhongtang():
	""" 中堂 """
	zq_name = '中堂镇'
	url = fs[zq_name]
	data=requests.get(url, headers=headers).text
	data = PyQuery(data)
	divs = data('.list-right_title.fon_1')
	res = []
	for i in divs:
		try:
			res2 = []
			i2 = i.findall('a')[0]
			name = i2.text  # 项目名称
			if '招标' not in name:
				continue

			url2 = i2.attrib.get('href')  # 项目地址
			if url2 in LS_url:
				continue
			# print(name,url)
			res2.append(name)
			res2.append(url2)

			data2 = requests.get(url2, headers=headers).text
			data2 = PyQuery(data2)
			fbrq = data2("publishtime:contains('202')")  # 发布日期
			fbrq = fbrq[0].text if fbrq else ''
			fbrq = fbrq.strip() if fbrq else ''
			res2.append(fbrq)
			zbbh = get_zbbhs(data2)
			res2.append(zbbh)

			jes = get_tzje(data2)  # 金额（包括投资金和担保金）
			res2.append(jes)
			tzzz = get_tzzz(data2)
			res2.append(tzzz)
			zbwj = get_zbwjs(data2)  # 招标文件获取方式
			res2.append(zbwj)
			jzsj = get_jzsjs(data2)

			res2.append(jzsj)
			res2.append(zq_name)
			res.append(res2)
			time.sleep(delayed)

			s = requests.session()
			s.keep_alive = False

		except Exception as e:
			print(zq_name, e)

	return res


def get_wnd():
	""" 望牛墩 """
	zq_name = '望牛墩镇'
	url = fs[zq_name]
	burl = get_burl(url)
	data=requests.get(url, headers=headers).text
	data = PyQuery(data)
	divs = data('.news_list_ty>li')
	res = []
	for i in divs:
		try:
			res2 = []
			i2 = i.findall('a')[0]
			url2 = i2.attrib.get('href')  # 项目地址
			if url2[:4] != 'http':
				url2 = burl + url2
			if url2 in LS_url:
				continue
			name = i2.text  # 项目名称
			# print(name,url)
			res2.append(name)
			res2.append(url2)
			data2 = requests.get(url2, headers=headers).text
			data2 = PyQuery(data2)
			fbrq = data2("b:contains('202')")  # 发布日期
			fbrq = fbrq[0].text if fbrq else ''
			res2.append(fbrq)
			zbbh = get_zbbhs(data2)
			res2.append(zbbh)
			jes = get_tzje(data2)  # 金额（包括投资金和担保金）
			res2.append(jes)
			tzzz = get_tzzz(data2)
			res2.append(tzzz)
			zbwj = get_zbwjs(data2)  # 招标文件获取方式
			res2.append(zbwj)
			jzsj = get_jzsjs(data2)

			res2.append(jzsj)
			res2.append(zq_name)
			res.append(res2)
			time.sleep(delayed)

			s = requests.session()
			s.keep_alive = False

		except Exception as e:
			print(zq_name, e)

	return res


def get_wanjiang():
	""" 万江街道 """
	zq_name = '万江街道'
	url = fs[zq_name]
	data=requests.get(url, headers=headers).text
	data = PyQuery(data)
	divs = data('.list-right_title.fon_1')
	res = []
	for i in divs:
		try:
			res2 = []
			i2 = i.findall('a')[0]
			url2 = i2.attrib.get('href')  # 项目地址
			if url2 in LS_url:
				continue
			name = i2.text  # 项目名称
			# print(name,url)
			res2.append(name)
			res2.append(url2)
			data2 = requests.get(url2, headers=headers).text
			data2 = PyQuery(data2)
			fbrq = data2("publishtime:contains('202')")  # 发布日期
			fbrq = fbrq[0].text if fbrq else ''
			res2.append(fbrq)
			zbbh = get_zbbhs(data2)
			res2.append(zbbh)
			jes = get_tzje(data2)  # 金额（包括投资金和担保金）
			res2.append(jes)
			tzzz = get_tzzz(data2)
			res2.append(tzzz)
			zbwj = get_zbwjs(data2)  # 招标文件获取方式
			res2.append(zbwj)
			jzsj = get_jzsjs(data2)

			res2.append(jzsj)
			res2.append(zq_name)
			res.append(res2)
			time.sleep(delayed)

			s = requests.session()
			s.keep_alive = False

		except Exception as e:
			print(zq_name, e)

	return res


def get_zhongshan():
	""" 中山市 """
	zq_name = '中山市'
	url = fs[zq_name]
	data=requests.get(url, headers=headers).text
	burl = get_burl(url)  # 主页
	page = '/Application/NewPage/ggnr.jsp?'  # 招标公告页
	divs = re.findall('<a href="(.*?)" target="_blank" title="(.*?)"', data)
	res = []
	for i in divs:
		try:
			res2 = []
			url2 = i[0]  # 项目地址
			url2 = burl + page + url2.split('?')[-1]
			if url2 in LS_url:
				continue
			name = i[1]  # 项目名称
			# print(name,url)
			res2.append(name)
			res2.append(url2)
			data2 = requests.get(url2, headers=headers).text
			# data2 = PyQuery(data2)
			fbrq = re.findall('<td colspan="3">(.*?)</td>', data2)  # 发布日期
			fbrq = fbrq[0] if fbrq else ''
			res2.append(fbrq)
			zbbh = ''  # 招标编号

			res2.append(zbbh)
			jes = get_tzje(data2)  # 金额（包括投资金和担保金）
			res2.append(jes)
			tzzz = get_tzzz(data2)

			res2.append(tzzz)
			zbwj = get_zbwjs(data2)  # 招标文件获取方式
			res2.append(zbwj)
			jzsj = re.findall('<td>(.*?)</td>', data2)
			if len(jzsj) >= 6:
				jzsj = jzsj[5]
			else:
				jzsj = ''
			res2.append(jzsj)
			res2.append(zq_name)
			res.append(res2)
			time.sleep(delayed)

			s = requests.session()
			s.keep_alive = False	

		except Exception as e:
			print(zq_name, e)

	return res


def get_zhangzhou():
	""" 漳州市 """
	zq_name = '漳州市'  # 镇区
	url = fs[zq_name]
	burl = get_burl(url)
	data=requests.get(url, headers=headers).text
	data = PyQuery(data)
	divs = data('tr[height="22"]')
	res = []
	for i in divs:
		try:
			res2 = []
			i2 = i.findall('td')

			url2 = i2[1].findall('a')[0].attrib.get('href')  # 项目地址
			if url2[:4] != 'http':
				url2 = burl + url2
			if url2 in LS_url:
				continue
			name = i2[1].text_content()  # 项目名称
			# print(name,url)
			res2.append(name)
			res2.append(url2)
			data2 = requests.get(url2, headers=headers).text
			data2 = PyQuery(data2)
			fbrq = i2[2].text_content()  # 发布日期
			res2.append(fbrq)
			zbbh = ''

			res2.append(zbbh)
			jes = get_tzje(data2)  # 金额（包括投资金和担保金）
			res2.append(jes)
			tzzz = get_tzzz(data2)
			res2.append(tzzz)
			zbwj = get_zbwjs(data2)  # 招标文件获取方式
			res2.append(zbwj)
			jzsj = get_jzsjs(data2)

			res2.append(jzsj)
			res2.append(zq_name)
			res.append(res2)
			time.sleep(delayed)

			s = requests.session()
			s.keep_alive = False


		except Exception as e:
			print(zq_name, e)

	return res



def main():
	global LS_url
	ld = pd.DataFrame()
	if os.path.isfile(file_name):
		file_name_new = get_file_new(file_name)  # 获取最新的文件
		ld = pd.read_excel(file_name_new)
		LS_url = set(ld['URL地址'])
	print(f'执行数据获取！ [{str(datetime.datetime.now())[:19]}]')
	res1 = get_zhongtang()
	res2 = get_wnd()
	res3 = get_wanjiang()
	res4 = get_zhongshan()
	res5 = get_zhangzhou()
	res6 = get_alls()

	res_all = res1 + res2 + res3 + res4 + res5 + res6
	gxcount = 0
	if res_all:
		d = pd.DataFrame(res_all, columns=['项目名称', 'URL地址', '发布日期', '招标编号', '金额', '资质', '招标文件获取方式', '截止时间', '镇区'])
		try:
			d = d[['发布日期', '截止时间', '项目名称', 'URL地址', '招标编号', '金额', '资质', '招标文件获取方式', '镇区']]
			d['发布日期'] = d['发布日期'].apply(lambda x: x.replace('\n', '').strip().split(': ')[-1][:10])
			d = ld.append(d)
			d.sort_values(by=['发布日期'], ascending=False, axis=0, inplace=True)

			gxcount = len(res_all)
		except Exception as e:
			print('error main', e)
		try:
			d.to_excel(file_name, index=False)
		except Exception as e:
			d.to_excel(f"{file_name[:-5]}_{str(datetime.datetime.now())[:16].replace(':','').replace(' ','')}.xlsx", index=False)
	print(f'更新：{gxcount} 条  [{str(datetime.datetime.now())[:19]}]')


if __name__ == '__main__':
	zxs = 0
	main()
	zxs = str(datetime.datetime.now())[:13]
	while True:
		t = str(datetime.datetime.now())[:13]
		th = t[-2:]
		if th in {'10', '12', '14', '16', '18'} and t != zxs:
			main()
			zxs = t
		time.sleep(120)