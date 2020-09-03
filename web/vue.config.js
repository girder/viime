/* eslint-disable */
const path = require('path');
const webpack = require('webpack');

const proxyTarget = 'http://localhost:5000';

let COMMITHASH = null;

if (process.env.NODE_ENV == 'production') {
  const GitRevisionPlugin = require('git-revision-webpack-plugin');
  const gitRevisionPlugin = new GitRevisionPlugin();
  COMMITHASH = JSON.stringify(gitRevisionPlugin.commithash());
}

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
      new webpack.DefinePlugin({ COMMITHASH }),
    ],
  },
  chainWebpack: (config) => {
    config.resolve.set('symlinks', false);
  },
};
