/* eslint-disable */
const path = require('path');
const GitRevisionPlugin = require('git-revision-webpack-plugin');
const webpack = require('webpack');

const gitRevisionPlugin = new GitRevisionPlugin();
const proxyTarget = 'http://localhost:5000';

module.exports = {
  lintOnSave: false,
  publicPath: '/',
  devServer: {
    proxy: {
      '/api': {
        target: proxyTarget,
      },
    },
    disableHostCheck: true,
  },
  configureWebpack: {
    resolve: {
      alias: {
        vue$: path.resolve(__dirname, './node_modules/vue/dist/vue.esm.js'),
      },
    },
    plugins: [
      new webpack.DefinePlugin({
        COMMITHASH: JSON.stringify(gitRevisionPlugin.commithash()),
      }),
    ],
  },
  chainWebpack: (config) => {
    config.resolve.set('symlinks', false);
  },
};
