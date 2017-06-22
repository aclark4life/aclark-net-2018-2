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
    // filename: 'aclarknet-bundle-[name]-[hash].js'
    filename: 'aclarknet-bundle.js'
  },
  plugins: [
      //tells webpack where to store data about your bundles.
      new BundleTracker({filename: './webpack-stats.json'}), 
      //makes jQuery available in every module
      new webpack.ProvidePlugin({ 
          $: 'jquery',
          jQuery: 'jquery',
          'window.jQuery': 'jquery' 
      })
  ],
  module: {
      loaders: [
          //a regexp that tells webpack use the following loaders on all 
          //.js and .jsx files
          {test: /\.jsx?$/, 
              //we definitely don't want babel to transpile all the files in 
              //node_modules. That would take a long time.
              exclude: /node_modules/, 
              //use the babel loader 
              loader: 'babel-loader', 
              query: {
                  //specify that we will be dealing with React code
                  presets: ['react'] 
              }
          }
      ]
  },
  resolve: {
      //tells webpack where to look for modules
      // modulesDirectories: ['node_modules'],
      //extensions that should be used to resolve modules
      // extensions: ['', '.js', '.jsx'] 
  }   
}
