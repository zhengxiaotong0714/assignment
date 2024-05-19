config = {
  "ret":r"D:\Python\Jupyter\AlgoTrade\assignment_zxt\data\next_ret\next_ret.pkl",
  "barra_dir": "/home/quant/work/data/barra_data",

  "date":{
    "start_date": "2021-01-01",
    "end_date": "2023-12-31"
  },

  "factors": [
    # {
    #   "factor_id": "factor_zxt006_1",
    #   "factor_values_file": r"D:\Python\Jupyter\AlgoTrade\assignment_zxt\code\calc_factor_codes\factor_model_zxt006\factor_values\factor_zxt006_1.csv",
    #   "result_save_path": r"D:\Python\Jupyter\AlgoTrade\assignment_zxt\code\calc_factor_codes\factor_model_zxt006\backtest_result",
    #   "weights": "rank",  # "alpha"
    #   "mode": "simple",  # "complex"
    #   "barra": False
    # },

    {
      "factor_id": "factor_zxt006_2_capsec",
      "factor_values_file": r"D:\Python\Jupyter\AlgoTrade\assignment_zxt\code\calc_factor_codes\factor_model_zxt006\factor_values\factor_zxt006_2_capsec.csv",
      "result_save_path": r"D:\Python\Jupyter\AlgoTrade\assignment_zxt\code\calc_factor_codes\factor_model_zxt006\backtest_result",
      "weights": "rank",  # "alpha"
      "mode": "simple",  # "complex"
      "barra": False
    },
    # {
    #   "factor_id": "factor_zxt006_3",
    #   "factor_values_file": r"D:\Python\Jupyter\AlgoTrade\assignment_zxt\code\calc_factor_codes\factor_model_zxt006\factor_values\factor_zxt006_3.csv",
    #   "result_save_path": r"D:\Python\Jupyter\AlgoTrade\assignment_zxt\code\calc_factor_codes\factor_model_zxt006\backtest_result",
    #   "weights": "rank",  # "alpha"
    #   "mode": "simple",  # "complex"
    #   "barra": False
    # },


  ]
}