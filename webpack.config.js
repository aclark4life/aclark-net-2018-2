// http://geezhawk.github.io/using-react-with-django-rest-framework
// https://webpack.js.org

//require our dependencies

var path = require('path')
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

module.exports = {
  entry: './aclarknet/static/app.js',
  output: {
    filename: 'aclarknet/static/aclarknet-bundle.js'
  }
}
