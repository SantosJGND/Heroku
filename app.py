# Import required libraries
import os
from random import randint

import plotly.plotly as py
from plotly.graph_objs import *

import flask
import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go

import plotly.figure_factory as ff

import pandas as pd


app = dash.Dash(__name__)
server = app.server

app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/dZVMbK.css'})


### Import data sets
#ID= sys.argv[1]
#Where = sys.argv[2]
#ref= sys.argv[3]

ID = 'PAG'
Where = "1"
ref = 'Indica'
###

Home = ref + "_regions/"

df = pd.read_csv(Home + 'DIM_private_'+ ref +'_request_CHR'+ Where +'.'+ID+'.txt',sep= '\t',header= None)

cluster_pca = pd.read_csv(Home + 'DIM_private_'+ref+'_comp_CHR'+Where+'.'+ID+'.txt',sep= '\t',header= None)

orderCore= pd.read_csv('Order_core_csv.txt')

vectors = pd.read_csv(Home + "Profile_"+ref+"_CHR"+Where+"."+ID+".txt",sep= '\t')

print(orderCore.head())


print(df.head())
#print(orderCore.head())
#### color reference

color_ref= ['red','yellow','blue','black','green','purple','orange','deepskyblue2','grey','darkolivegreen1','navy','chartreuse','darkorchid3','goldenrod2']

pop_refs = ["Indica","cAus","Japonica","GAP","cBasmati","Admix"]

### Vectors and names

#Code_choices= ['Full_colors','red','yellow','blue','black','orange','purple','green','deepskyblue2','red3','darkolivegreen1']

Code_choices = [color_ref[len(vectors.columns)-x-1] for x in range(len(vectors.columns))]
Code_choices.extend(["Full_colors"]) 
Code_choices = Code_choices[::-1]


#### Prepqre Dash apps

app.layout = html.Div([
    
    
    html.Div([
    html.H4(
    id= "header1",className= "six columns",children= "Feature space"
    ),
    html.H4(
    id= "header2",className= "six columns",children= "selected accessions"
    )    
    ],className= "row"),
    
    
    html.Div([
    dcc.Graph(id='local_pca', className='six columns',animate = True),
    html.Div(id='table-content', className='six columns')
    ],className='row'),
    
    html.Hr(),
    
    html.Div([
    html.H5(
    id= "header1",className= "six columns",children= "opacity"
    ),
    html.H5(
    id= "header2",className= "six columns",children= "Likelihood threshold"
    )    
    ],className= "row"),
    
    html.Div([

    dcc.Slider(
    updatemode= "drag",
    className='six columns',
    id = 'opacity',
    min = .1,
    max = 1,
    value = .8,
    step = .1,
    #marks = [str(.1*x) for x in range(1,10)]
    ),
    dcc.Slider(
    updatemode= "drag",
    className= "six columns",
    id= "threshold",
    min= .05,
    max= 1,
    value= .2,
    step= .05
    )
    ],className='row'),
    
    html.Hr(),
    
    html.Div([
    html.H5(children= 'Chose a color')
    ],className= "row"),
    
    html.Div([
    dcc.Dropdown(
    className='six columns',
    id = 'chose_color',
    value = 0,
    options = [{"label":x,"value": x} for x in range(len(Code_choices))]
    )
    ],className= "row"),
    
    html.Hr(),
    
    html.Div([
    dcc.Graph(id = "clusters",className="six columns",figure= {
            'data': [go.Scatter3d(
            x = cluster_pca[cluster_pca[0] == i][3],
            y = cluster_pca[cluster_pca[0] == i][4],
            z = cluster_pca[cluster_pca[0] == i][5],
            type='scatter3d',
            mode= "markers",
        marker= {
#            'color': [color_ref[x] for x in cluster_pca[0]],
#            'color': cluster_pca[0],
            'line': {'width': 0},
            'size': 4,
            'symbol': 'circle',
            'opacity': .8
          },
          name = i
        ) for i in cluster_pca[0].unique()],
        'layout': {
      "autosize": True, 
      "hovermode": "closest",
      "legend": {
        "x": 0.873529411765, 
        "y": 0.877829326396, 
        "borderwidth": 1, 
        "font": {"size": 13}
      },
      "scene": {
        "aspectmode": "auto", 
        "aspectratio": {
          "x": 1.02391505715, 
          "y": 0.737436541286, 
          "z": 1.3243763495
        }, 
        "camera": {
          "center": {
            "x": 0, 
            "y": 0, 
            "z": 0
          }, 
          "eye": {
            "x": 1.80578427889, 
            "y": 1.17729688569, 
            "z": 0.201532084509
          }, 
          "up": {
            "x": 0, 
            "y": 0, 
            "z": 1
          }
        }, 
        "xaxis": {
          "title": "PC1", 
          "type": "linear"
        }, 
        "yaxis": {
          "title": "PC2", 
          "type": "linear"
        }, 
        "zaxis": {
          "title": "PC3", 
          "type": "linear"
        }
      }, 
      "showlegend": True, 
      "title": "<b>clusters - observations</b>", 
      "xaxis": {"title": "V3"}, 
      "yaxis": {"title": "V2"}
    }
    }
    ),
    dcc.Graph(id= "density_plot",className= "six columns")
    ])
])



def generate_table(dataframe):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(len(dataframe))]
    )


@app.callback(
   Output('density_plot','figure'),
    [Input('chose_color','value')])
def update_density(selected_group):
    if selected_group != 0:
        dense_plot=  ff.create_distplot([vectors.iloc[:,selected_group-1]], [color_ref[selected_group-1]])
        dense_plot['layout'].update(title='<b>likelihood density</b>')
        return dense_plot

@app.callback(
    Output('table-content','children'),
    [Input('chose_color','value'),
     Input('threshold','value')])
def update_table(selected_group,threshold):
    if selected_group== 0:
        show_table = [x for x in range(len(df))]
    else:
        show_table = [x for x in range(len(df)) if vectors.iloc[x,selected_group-1] >= threshold]
    return html.Div(
        children= generate_table(orderCore[["ID","NAME","COUNTRY","Initial_subpop"]].iloc[show_table,:]),
        style={
            'overflowX': 'scroll',
            'overflowY': 'scroll',
            'height': '450px',
            'display': 'block',
            'paddingLeft': '15px'
        }
)

@app.callback(
    Output(component_id= 'local_pca',component_property = 'figure'),
    [Input(component_id= 'chose_color',component_property = 'value'),
     Input(component_id= 'opacity',component_property= 'value'),
    Input(component_id= "threshold",component_property= "value")])
def update_figure(selected_column,opac,threshold):
    if selected_column == 0:
        scheme = [color_ref[x] for x in df[0]]
    else:
        scheme = [["grey","red"][int(x>=threshold)] for x in vectors.iloc[:,selected_column-1]]
    return {
    'data': [go.Scatter3d(
        x = df[df[0] == i][2],
        y = df[df[0] == i][3],
        z = df[df[0] == i][4],
        type='scatter3d',
        mode= "markers",
        text= orderCore[["ID","NAME","COUNTRY","Initial_subpop"]].apply(lambda lbgf: (
      "<b>{}</b><br>Name: {}<br>Country: {}<br>{}".format(lbgf[0],lbgf[1],lbgf[2],lbgf[3])),
        axis= 1),
    marker= {
#        'color': scheme,
        'color': color_ref[i],
        'line': {'width': 0},
        'size': 4,
        'symbol': 'circle',
      "opacity": opac
      },
      name= pop_refs[i]
    ) for i in df[0].unique()],
    'layout': {
  "autosize": True, 
  "hovermode": "closest",
  "legend": {
  "x": 0.798366013072, 
  "y": 0.786064620514, 
  "borderwidth": 1, 
  "font": {"size": 13}
      },
  "margin": {
    "r": 40, 
    "t": 50, 
    "b": 20, 
    "l": 30, 
    "pad": 0
  }, 
  "scene": {
    "aspectmode": "auto", 
    "aspectratio": {
      "x": 1.02391505715, 
      "y": 0.737436541286, 
      "z": 1.3243763495
    }, 
    "camera": {
      "center": {
        "x": 0, 
        "y": 0, 
        "z": 0
      }, 
      "eye": {
        "x": 1.80578427889, 
        "y": 1.17729688569, 
        "z": 0.201532084509
      }, 
      "up": {
        "x": 0, 
        "y": 0, 
        "z": 1
      }
    }, 
    "xaxis": {
      "title": "PC1", 
      "type": "linear"
    }, 
    "yaxis": {
      "title": "PC2", 
      "type": "linear"
    }, 
    "zaxis": {
      "title": "PC3", 
      "type": "linear"
    }
  }, 
  "showlegend": True, 
  "title": "<b>Accessions - loadings</b>", 
  "xaxis": {"title": "V3"}, 
  "yaxis": {"title": "V2"}
}
}


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
