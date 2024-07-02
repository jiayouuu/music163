from py import get_analyze as ga
#第一个参数为榜单类型(0为热歌榜，1为飙升榜，2为新歌榜，3为原创榜)
#第二个参数为爬取榜单内的歌曲数目
#第三个参数为爬取一首歌内的总评论数
#第四个参数为一次爬取的评论数(步进)，默认为50
if __name__=='__main__':
    ga.get_all(toplist=2,songslength=3,commentslength=120,onece=50)
