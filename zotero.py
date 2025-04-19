
import os
from pyzotero import zotero


def get_zotero_corpus(id:str,key:str) -> list[dict]:
    """
    定义一个函数，用于从 Zotero 获取文献语料库
    参数:
    id (str): Zotero 用户的 ID
    key (str): Zotero 用户的 API 密钥
    返回:
    list[dict]: 包含文献信息的字典列表
    """
    # 创建一个 Zotero 实例，用于与 Zotero API 进行交互
    zot = zotero.Zotero(id, 'user', key)
    # 获取用户的所有集合，并遍历所有分页以获取完整结果
    collections = zot.everything(zot.collections())
    # 将集合列表转换为字典，键为集合的 key，值为集合对象
    collections = {c['key']:c for c in collections}
    # 获取所有会议论文、期刊文章和预印本类型的文献，并遍历所有分页以获取完整结果
    corpus = zot.everything(zot.items(itemType='conferencePaper || journalArticle || preprint'))
    # 过滤掉没有摘要的文献
    corpus = [c for c in corpus if c['data']['abstractNote'] != '']

    # 定义一个内部递归函数，用于获取集合的完整路径
    # 参数:
    #   col_key (str): 集合的 key
    # 返回:
    #   str: 集合的完整路径
    def get_collection_path(col_key:str) -> str:
        # 检查集合是否有父集合
        if p := collections[col_key]['data']['parentCollection']:
            # 若有父集合，则递归调用函数获取父集合路径，并拼接当前集合名称
            return get_collection_path(p) + '/' + collections[col_key]['data']['name']
        else:
            # 若没有父集合，则返回当前集合名称
            return collections[col_key]['data']['name']

    # 遍历语料库中的每篇文献
    for c in corpus:
        # 为每篇文献获取其所在集合的完整路径列表
        paths = [get_collection_path(col) for col in c['data']['collections']]
        # 将集合路径列表添加到文献信息字典中
        c['paths'] = paths

    return corpus

if __name__ == '__main__':
    id = os.environ['ZOTERO_ID']
    key = os.environ['ZOTERO_KEY']
    corpus = get_zotero_corpus(id,key)