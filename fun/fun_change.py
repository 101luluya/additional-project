# -*- coding: utf-8 -*-

# 外部功能函数，包含模型训练，预测，文件存储等功能对应的函数
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from matplotlib import pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import GridSearchCV
import tensorflow as tf
from sklearn.metrics import make_scorer
import os

current_path = os.path.dirname(__file__)  # 先找到当前文件所在的目录ui
father_path = os.path.dirname(current_path)  # 往上倒一层目录,也就是 ui所在的文件夹，项目文件夹 的绝对路径


# 作为模块调用时，利用 father_path 可以保证，相对路径得到的结果不会错误

# 将预测结果写入文件函数 先读取已经选择环境数据的表格，增加预测结果列，保存
def write_tofile(fpath_data, fpath_save, data_add):
    data = pd.read_excel(fpath_data)
    # print(data)
    data['Power(MW)'] = data_add
    # print(data)
    data.to_excel(fpath_save)


# 新定义一个划分集合的函数，为了方便后面的模型函数的实现
def split_x_and_y(array, days_used_to_train):
    features = list()
    labels = list()

    for i in range(days_used_to_train, len(array)):
        features.append(array[i - days_used_to_train:i, :-1])
        labels.append(array[i, -1])
    return np.array(features), np.array(labels)


# 用于训练和预测的函数
def model_training(path, isFD):
    if isFD:
        path1 = os.path.join(father_path, 'train_data/FD001/03 His_NWP_FD.xlsx')
        path2 = os.path.join(father_path, 'train_data/FD001/02 His_Power_FD.xlsx')
        traindays = 4
        maxrange = 3
        shape2 = 15
    else:
        path1 = os.path.join(father_path, 'train_data/GF001/03 His_NWP_GF.xlsx')
        path2 = os.path.join(father_path, 'train_data/GF001/02 His_Power_GF.xlsx')
        traindays = 4
        maxrange = 3
        shape2 = 6

    try:
        predf = pd.read_excel(path).drop('Datetime', axis=1)
        scaler = MinMaxScaler()
        scaler = scaler.fit(predf)
        predf = scaler.transform(predf)

        # print(predf.shape)

        # 得对df_处理成三维的格式
        def deal_df(array, traindays):
            features = list()

            for i in range(traindays, len(array)):
                features.append(array[i - traindays:i, :])

            return np.array(features)

        # df_=deal_df(predf,traindays)
        # print(df_.shape)
        df1 = pd.read_excel(path1).drop('Datetime', axis=1)
        df2 = pd.read_excel(path2).drop('Datetime', axis=1)
        df = pd.concat([df1, df2], axis=1)
        df_train = df[:int(0.85 * len(df))]
        df_valid = df[int(0.85 * len(df)):int(0.89 * len(df))]
        df_test = df[int(0.88 * len(df)):]

        for i in range(0, maxrange):
            scaler = MinMaxScaler()
            scaler = scaler.fit(df_train)
            df_train = scaler.transform(df_train)
            train_ = df_train.copy()
            df_valid = scaler.transform(df_valid)
            valid_ = df_valid.copy()
            df_test = scaler.transform(df_test)
            test_ = df_test.copy()
            df_ = deal_df(predf, traindays)
            train_X, train_y = split_x_and_y(df_train, traindays)
            valid_X, valid_y = split_x_and_y(df_valid, traindays)
            test_X, test_y = split_x_and_y(df_test, traindays)

            def ev(y_true, y_predict):
                difference = ((np.array(y_true) - np.array(y_predict.flatten())) ** 2).sum()
                return float(difference)
                from sklearn.metrics import make_scorer

            my_scorer = make_scorer(ev, greater_is_better=False)
            scoring = {
                'ev': my_scorer
            }

            # 建立模型函数
            def build_model(size):
                tf.random.set_seed(1)  # 设置随机数种子
                # Create grid_model
                grid_model = tf.keras.Sequential()
                grid_model.add(tf.keras.layers.LSTM(units=64))
                grid_model.add(tf.keras.layers.Dense(64))
                grid_model.add(tf.keras.layers.Dense(size))
                grid_model.add(tf.keras.layers.Dense(1))

                # Compile the grid_model
                grid_model.compile(
                    optimizer='adam',
                    loss='mse')

                return grid_model
                from keras.wrappers.scikit_learn import KerasClassifier

            grid_model = KerasRegressor(build_fn=build_model)
            parameters = {'batch_size': [16], 'epochs': [40], 'size': [32]}
            grid_search = GridSearchCV(estimator=grid_model,
                                       param_grid=parameters,
                                       scoring=scoring,
                                       refit='ev',
                                       n_jobs=1,
                                       cv=2)
            grid_search = grid_search.fit(train_X, train_y, validation_data=(valid_X, valid_y))
            # 输出最佳模型为my_model
            model = grid_search.best_estimator_.model
            pred_train = model.predict(train_X)
            pred_valid = model.predict(valid_X)
            pred_test = model.predict(test_X)
            pred_df = model.predict(df_)
            # df_train = np.hstack((df_train[traindays:, :-1], pred_train))
            # df_train = np.hstack((df_train, np.mat(train_[traindays * (i + 1):, -1]).T))
            # df_valid = np.hstack((df_valid[traindays:, :-1], pred_valid))
            # df_valid = np.hstack((df_valid, np.mat(valid_[traindays * (i + 1):, -1]).T))
            # df_test = np.hstack((df_test[traindays:, :-1], pred_test))
            # df_test = np.hstack((df_test, np.mat(test_[traindays * (i + 1):, -1]).T))
            # predf = np.hstack((predf[traindays:, :], pred_df))
            df_train = np.hstack((df_train[traindays:, :-1], pred_train))
            df_train = np.hstack((df_train, np.mat(train_[traindays:, -1]).T))
            df_valid = np.hstack((df_valid[traindays:, :-1], pred_valid))
            df_valid = np.hstack((df_valid, np.mat(valid_[traindays:, -1]).T))
            df_test = np.hstack((df_test[traindays:, :-1], pred_test))
            df_test = np.hstack((df_test, np.mat(test_[traindays:, -1]).T))
            predf = np.hstack((predf[traindays:, :], pred_df))
            predf = scaler.inverse_transform(predf)
            result = predf[:, -1].copy()
            predf = scaler.transform(predf)
            exchange1 = scaler.inverse_transform(df_train[:, :-1])
            exchage2 = scaler.inverse_transform(np.hstack((df_train[:, :-2], np.mat(df_train[:, -1]))))
            df_train = np.hstack((exchange1, np.mat(exchage2[:, -1]).T))
            exchange1 = scaler.inverse_transform(df_valid[:, :-1])
            exchage2 = scaler.inverse_transform(np.hstack((df_valid[:, :-2], np.mat(df_valid[:, -1]))))
            df_valid = np.hstack((exchange1, np.mat(exchage2[:, -1]).T))
            exchange1 = scaler.inverse_transform(df_test[:, :-1])
            exchage2 = scaler.inverse_transform(np.hstack((df_test[:, :-2], np.mat(df_test[:, -1]))))
            df_test = np.hstack((exchange1, np.mat(exchage2[:, -1]).T))

        print(1)
        print(result)
        plt.plot(range(len(result)), result, label='Prediction')
        plt.xlabel('Amount of samples', size=15)
        plt.ylabel('Prediction')
        plt.legend()
        if isFD:
            if os.path.exists(os.path.join(father_path, 'temp/temp_FD.jpg')):
                os.remove(os.path.join(father_path, 'temp/temp_FD.jpg'))
            plt.savefig(os.path.join(father_path, 'temp/temp_FD.jpg'))
        else:
            if os.path.exists(os.path.join(father_path, 'temp/temp_GF.jpg')):
                os.remove(os.path.join(father_path, 'temp/temp_GF.jpg'))
            plt.savefig(os.path.join(father_path, 'temp/temp_GF.jpg'))
        plt.close()
        return [i for i in result]
    except:
        return []


# 点预测函数 由于发电数据通过单点环境预测比较困难，同时模型预测结果受环境数据归一化后结果影响较大，且单点前后环境无法确定
# 点预测采用查找表法   精度可以由error参数和最大扩大轮数控制
def point_predict(data_list, isFD):
    # data_list = [15, 7.915, 29.1882, 28.54, 999, 85.76]
    # data_list=[3.9845, 295, 4.128, 296, 4.2635, 299, 4.3822, 301, 4.4963, 302, 4.5447, 303, 29.5, 1004.25, 0]
    i = 0
    # print(data_list)

    data_result = pd.Series([], dtype='float64')
    # data_result = pd.DataFrame()

    if isFD:
        error_s_13 = 0.1
        error_s_57 = 0.2
        error_s_91 = 0.5
        # error_d = 200
        # error_t = 10
        error_h = 0.5
        path = os.path.join(father_path, 'resource/Search_NWP_FD.xlsx')
        data_search = pd.read_excel(path).drop('Datetime', axis=1)
        # 部分参数对Power影响很小，忽略其影响
        while data_result.empty and i < 10:
            i += 1
            data_result = data_search['Power(MW)'][
                (data_search['Speed10'] + error_s_13 >= data_list[0]) & (
                            data_search['Speed10'] - error_s_13 < data_list[0])
                & (data_search['Speed30'] + error_s_13 >= data_list[2]) & (
                            data_search['Speed30'] - error_s_13 < data_list[2])
                & (data_search['Speed50'] + error_s_57 >= data_list[4]) & (
                            data_search['Speed50'] - error_s_57 < data_list[4])
                & (data_search['Speed70'] + error_s_57 >= data_list[6]) & (
                            data_search['Speed70'] - error_s_57 < data_list[6])
                & (data_search['Speed90'] + error_s_91 >= data_list[8]) & (
                            data_search['Speed90'] - error_s_91 < data_list[8])
                # &(data_search['Speed100'] + error_s_91 >= data_list[10]) & (data_search['Speed100'] - error_s_91 < data_list[10])
                # &(data_search['Direction10'] + error_d >= data_list[1]) & (data_search['Direction10'] - error_d < data_list[1])
                # & (data_search['Direction30'] + error_d >= data_list[3]) & (data_search['Direction30'] - error_d < data_list[3])
                # & (data_search['Direction50'] + error_d >= data_list[5]) & (data_search['Direction50'] - error_d < data_list[5])
                # & (data_search['Direction70'] + error_d >= data_list[7]) & (data_search['Direction70'] - error_d < data_list[7])
                # & (data_search['Direction90'] + error_d >= data_list[9]) & (data_search['Direction90'] - error_d < data_list[9])
                # & (data_search['Direction100'] + error_d >= data_list[11]) & (data_search['Direction100'] - error_d < data_list[11])
                # &(data_search['Temper'] + error_t >= data_list[12]) & (data_search['Temper'] - error_t < data_list[12])
                & (data_search['Humidity'] + error_h >= data_list[14]) & (
                            data_search['Humidity'] - error_h < data_list[14])
                ]
            # print("e{}:  {}".format(i, data_result))
            error_s_13 += 0.1
            error_s_57 += 0.2
            error_s_91 += 0.5
            # error_d += 2
            # error_t += 0.1
            error_h += 0.5

    else:
        error_h = 0.5
        error_i = 1
        path = os.path.join(father_path, 'resource/Search_NWP_GF.xlsx')
        data_search = pd.read_excel(path).drop('Datetime', axis=1)
        # print(data_search)
        # 部分参数对Power影响很小，忽略其影响
        while data_result.empty and i < 10:
            i += 1
            data_result = data_search['Power(MW)'][
                (data_search['Humidity'] + error_h >= data_list[5]) & (data_search['Humidity'] - error_h < data_list[5])
                & (data_search['Irradiance'] + error_i >= data_list[0]) & (
                            data_search['Irradiance'] - error_i < data_list[0])
                ]
            # print("e{}:  {}".format(i, data_result))
            error_h += 0.5
            error_i += 2

    data_result_list = data_result.values.tolist()
    # print('result:  {}'.format(data_result_list))
    # 将查找匹配到的值求平均输出，没有匹配到结果则返回False以供判断
    if data_result_list:
        # print('result_back:  {}'.format(sum(data_result_list) / len(data_result_list)))
        return round(sum(data_result_list) / len(data_result_list), 2)
    else:
        # print('null')
        return False


if __name__ == "__main__":
    pass
