# Stock Lookbook

### Stock visualizations for the visual learners

Sometimes I am surprised at how ignorant I am about the stats of the stocks I have had over the past years. And, I know I am not the only one. For visual learners like me, I made a visualization of the performance, volatility, and valuation of stocks, which I believe are the three most basic things.

The height of the diagram represents performance and the width represents volatility over the past period. Intuitively, the higher the performance, the higher it is, and the more volatile, the thinner it is. Plus, the third attribute, price to earnings ratio, is expressed as a color, and it goes from pink to yellow as stock has a higher P/E.

Now, you can grasp the performance, volatility, and price tag of trending stocks at a glance at:  https://stocklookbook.azurewebsites.net/

![SCREEN_SHOT](./pictures/Screen-Shot-stock-lookbook.png)

## File Descriptions
- wsgi.py : start-up file to run the web app
- config.py: configuration for the web app
- requirments.txt: packages required to be installed 
- stocklookbookapp
    - model
        - dbmanager.py: ETL pipeline
        - stockdb.py: Define db models and wrangle data for visualizations
    - templates: html template files
    - static: required assets/scripts/files for the front-end
   
    



## Licensing, Acknowledgements

MIT License

## Credit

Developed by Kyou Hee Lee. Feel free to give comments or suggestions.

