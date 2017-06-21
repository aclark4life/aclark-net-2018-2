// http://geezhawk.github.io/using-react-with-django-rest-framework
// https://webpack.js.org

//require our dependencies

var path = require('path')
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

module.exports = {
  context: __dirname,
  entry: './aclarknet/static/app.js',
  output: {
    path: path.resolve('./aclarknet/static/'), 
    filename: 'aclarknet-bundle-[name]-[hash].js'
  }
}
