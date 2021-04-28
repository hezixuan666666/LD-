# 爬取东莞市、漳州市、中山市招标公告

爬取过程会有点长，大概半小时以上，可以慢慢等待。

如果第一次爬不出来，可以把中山地区的爬取过程注释掉，先爬东莞市和漳州市的，中山市的网站应该是有反爬机制，所以会报错：

```win
SSLError: HTTPSConnectionPool(host='ggzyjy.zs.gov.cn', port=443): Max retries exceeded with url: /Application/NewPage/PageSubItem.jsp?node=58 (Caused by SSLError(SSLError(1, '[SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1123)')))
```

如果有兴趣的可以试试代理IP，我最近比较忙，就不修改了，如果要运行不报错（把中山地区的注释掉即可）

爬取url之后可以对每周的招标公告有一个大致的了解，然后把招标文件的pdf下载下来，用正则表达式的方法对招标文件进行扫描，提取出招标文件中有用的信息。