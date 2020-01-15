MYSQL = {
    "master": "mysql+mysqldb://carol:carol@2019@192.168.0.11:3306/carol_test?charset=utf8mb4&binary_prefix=true",
    "slaves": [
        "mysql+mysqldb://carol:carol@2019@192.168.0.13:3306/carol_test?charset=utf8mb4&binary_prefix=true",
    ],
}

NOTE = {
    '15527842480': '@广告投放',
    '13581410621': '@精准招聘',
    '17092710112': '@精准招聘',
    '18571709593': '@普工',
    '13260595196': '@商超便利店',
    '18120256923': '@商超便利店',
}

SN_MAP = {
    '15527842480': '750BBLC2GHCW',
    '13581410621': '750BBKN2QBJZ',
    '17092710112': '750BBKN2QBJZ',
    '18571709593': '750BBL62NZBF',
    '13260595196': ''
}

SEND_ROLE = {
    '全部': [0, 1],
    '未邀请过': [0],
    '已邀请过': [1]
}