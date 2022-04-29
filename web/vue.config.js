/* eslint-disable */
const path = require('path');
const webpack = require('webpack');

const proxyTarget = 'http://localhost:5000';

function commitHashFromGit() {
  const GitRevisionPlugin = require('git-revision-webpack-plugin');
  const gitRevisionPlugin = new GitRevisionPlugin();
  try {
    return gitRevisionPlugin.commithash();
  } catch {
    return undefined;
  }
}

let commitHash;
if (process.env.NODE_ENV === 'production') {
  commitHash = commitHashFromGit();
  if (commitHash === undefined) {
    // Cloudflare Pages does not have an actual Git clone
    commitHash = process.env.CF_PAGES_COMMIT_SHA;
  }
}
if (commitHash === undefined) {
  commitHash = 'HEAD';
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
      new webpack.DefinePlugin({
        COMMITHASH: JSON.stringify(commitHash),
      }),
    ],
  },
  chainWebpack: (config) => {
    config.resolve.set('symlinks', false);
  },
};
