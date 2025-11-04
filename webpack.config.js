const path = require('path');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    entry: './src/index.js',
    output: {
      path: path.resolve(__dirname, 'static/js'),
      filename: isProduction ? '[name].[contenthash].js' : 'bundle.js',
      chunkFilename: '[name].[contenthash].chunk.js',
      clean: true,
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env', '@babel/preset-react'],
            },
          },
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader'],
        },
      ],
    },
    resolve: {
      extensions: ['.js', '.jsx'],
    },
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: 10,
          },
          react: {
            test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
            name: 'react-vendor',
            priority: 20,
          },
        },
      },
      usedExports: true,
      minimize: isProduction,
    },
    performance: {
      maxAssetSize: 300000,
      maxEntrypointSize: 300000,
      hints: isProduction ? 'warning' : false,
    },
    plugins: [
      // Uncomment to analyze bundle size (requires webpack-bundle-analyzer package)
      // const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
      // new BundleAnalyzerPlugin({ analyzerMode: 'static' }),
    ],
  };
};