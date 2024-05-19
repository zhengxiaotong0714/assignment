config = \
  {
  "dir":{
    "data_dir": r"D:\Python\Jupyter\AlgoTrade\assignment_zxt\data",
    "meta_dir": r"D:\Python\Jupyter\AlgoTrade\assignment_zxt\data\meta",
    "factor_model_files_dir": r"D:\Python\Jupyter\AlgoTrade\assignment_zxt\code\calc_factor_codes\factor_model_zxt006",#py文件所在目录
    "result_save_path": r"D:\Python\Jupyter\AlgoTrade\assignment_zxt\code\calc_factor_codes\factor_model_zxt006\factor_values"#运算结果存储路径
  },

  "date": {
    "start_date": "2021-01-01",
    "end_date": "2023-12-31"
  },

  "factors": [
    # {
    #   "factor_id": "factor_zxt006_1",#给你的因子取个名字，自定义的，不影响程序运行
    #   "factor_model_file": "factor_model_zxt006",#py文件文件名
    #   "params": {},#可选。你的因子计算需要的参数，如你的因子是近 m 天 价格和成交量的相关系数，在这里给出m的值。
    #   "operators":[]#可选。你的因子在初步计算完之后，是否需要做一个op，（如转换成横截面的序、时序的序、zscore、中性化等等）
    # },
    {
      "factor_id": "factor_zxt006_2_capsec",
      "factor_model_file": "factor_model_zxt006",
      "params": {},
      "operators": [
        {"name":"op_capsecneut","params":{}},#市值行业中性化
      ]
    }
    # {
    #   "factor_id": "factor_zxt006_3",
    #   "factor_model_file": "factor_model_zxt006",
    #   "params": {},
    #   "operators": [
    #     {"name":"op_capsecneut","params":{}},#这里再将因子转变成时序上近10天的序
    #     {"name": "op_neut", "params": {"risks" : "close"}},#再对价格、成交量做中性化
    #   ]
    # }
  ]
}