from dash import Dash, html,dash_table,dcc,callback,Output, Input
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import geopandas as gpd
import os
import dash_bootstrap_components as dbc
import io
import dash_leaflet as dl
import json


import base64


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


data1=gpd.read_file(r"kenya.gpkg")
town=gpd.read_file(r"town.gpkg")
town=town.to_crs(epsg=21037)
data1=data1.to_crs(epsg=21037)
dat=town.sjoin(data1,how='left',predicate='within')
dat=dat[['NAME_2','TOWN','geometry']]
dat=pd.pivot_table(dat,values='TOWN',index=['NAME_2'],aggfunc='count')
dat=dat.reset_index()


text1= "MINISTRY OF LANDS, PUBLIC WORKS,"
text2="HOUSING AND URBAN DEVELOPMENT"
text3="DIRECTORATE OF PHYSICAL PLANNING "
text4="CERTIFICATE\n"
text5="\nI certify that the plan has been prepared and\n published as per the requirements of the\n Physical and Land Use Planning ActNo. 13 of 2019"
text6="Name of Planner  ... . . . . . . . . .. . . . . .. . . .. . . . . . ... \n \n Sign.. .. . . . . . .. . . . . .. . .  Date . .. . . . . .. . ... . . . . .. \n"
text7="AMENDMENT"
text8="MINISTRY OF LANDS, PUBLIC WORKS,\n HOUSING AND URBAN DEVELOPMENT \n"
text9= "DIRECTORATE OF PHYSICAL PLANNING"
text10="KENYA"
text11="PART DEVELOPMENT PLAN"
text13=" DEPARTMENTAL REF. NUMBER ........"
text14=" CERTIFIED"
text15a="     _ _ _ _ _ _ _ _ _ _ _  _ _ _ _ _ _ _ _ _ __ _ _ _    _ _ _"
text15="     National Director of Physical Planning       Date"
text16="APPROVED"
text16a="        _ _ _ _ _ _ _ _ _ _ _  _ _ _ _ _ _ _ _ _ _ _ _ _ _             _ _ _"
text17= "        Cabinet Secretary for Lands , Public Works,         Date\n         Housing and Urban Development"
text18="APPROVED DEVELOPMENT PLAN NUMBER"

import matplotlib.patches as patches


app.layout = dbc.Container([
    html.Div(children="Geospatial Automation and Dashboard", style={'textAlign': 'center', 'color': 'blue', 'fontSize': 50}),
    
    dbc.Row([
        dbc.Col(html.Label("Choose the county to plot", style={'textAlign': 'center', 'color': 'red', 'fontSize': 30}), width=12)
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Dropdown(options=data1['NAME_2'].unique(), value="Nairobi", id="counties", style={'width': '100%'}), width=5)
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.Img(id='plot', style={'width': '100%', 'height': 'auto'}), width=12)
    ]),

    html.Br(),
    dbc.Row([
        dcc.Loading(
        id="loading",
        type="circle",
        children=[
            html.Div(id="content")
        ]
    ),
        dbc.Col(dash_table.DataTable(
            data=dat.to_dict('records'), 
            page_size=10, 
            style_table={'overflowX': 'auto'}, 
            style_cell={'textAlign': 'left'}
        ), width=11,align="center")
    ],justify="center"),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=px.histogram(dat, x='NAME_2', y='TOWN'), style={'width': '100%'}), width=10,align="center")
    ],justify="center"),
     html.Br(),

    dbc.Row([
        dbc.Col(dl.Map([
            dl.TileLayer(),
            dl.GeoJSON(id="geojson", options=dict(style=dict(color="blue"))),
            dl.GeoJSON(id="geojson1", options=dict(style=dict(color="blue")))
        ],
        id="leaflet-map",
        center=[0, 0],
        zoom=9,
        style={"height": "70vh", "width": "100%",'textAlign': 'center'}), width=10,
            align="center")
    ],justify="center"),

    html.Br(),
    dbc.Row([
        dbc.Col(html.Div(children="Let's take Geospatial and Survey to a new level", style={'textAlign': 'center', 'color': 'red', 'fontSize': 20}), width=12)
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.Label("Created By Kipyegon Amos", style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30}), width=12, className="text-center",align="center")
    ], className="mt-3")
], fluid=True)


@app.callback(
    Output("content", "children"),
    [Input("loading", "children")]
)
def update_content(_):
    return "Your"

@callback(
        Output(component_id='plot',component_property='src'),
           Output(component_id="geojson", component_property="data"),
           Output(component_id="geojson1", component_property="data"),
        Output(component_id="leaflet-map", component_property="center"),
        Input(component_id='counties',component_property='value')
        
)

def update_image(selected_county):
    data2=data1[data1['NAME_2']==selected_county]
    data3=data2.unary_union
    
    da=data2.to_crs(epsg=4326)
    geojson = json.loads(da.to_json())
    bounds = da.total_bounds  # [minx, miny, maxx, maxy]
   # [minx, miny, maxx, maxy]
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2
    center = [center_lat, center_lon]
    tao=town[town.geometry.within(data3)]
    ta=tao.to_crs(epsg=4326)
    geojson1 = json.loads(ta.to_json())

    minx, miny, maxx, maxy=data2.total_bounds 
    
    width, height = maxx - minx, maxy - miny
    area  = width * height


    map_width = maxx - minx  
    map_height = maxy - miny 

    a4_width_potrait, a4_height_potrait = 8.27, 11.69

    a4_width, a4_height =   11.69,8.27
    a4_width_in=a4_width
    a4_height_in=a4_height

    # Available scales
    scales = [100,500,1000, 2500, 5000, 10000, 25000, 50000,100000]

    # Calculate the real-world distances covered by A4 at each scale
    best_scale = None
    for scale in scales:
        # Calculate the real-world size that fits A4 at this scale
        width_at_scale = a4_width_in * scale  # in meters
        height_at_scale = a4_height_in * scale  # in meters
        
        # Check if the map fits within this scale
        if map_width <= width_at_scale and map_height <= height_at_scale:
            best_scale = scale
            break

    # Fallback if map is too large for the biggest scale
    if best_scale is None:
        best_scale = scales[-1]

    print(f"Selected scale: 1:{best_scale}")

    # Calculate the plot's bounds for the selected scale
    center_x, center_y = (minx + maxx) / 2, (miny + maxy) / 2
    plot_width = a4_width_in * best_scale
    plot_height = a4_height_in * best_scale
    # Set up plot
    fig, ax = plt.subplots(figsize=(a4_width_in, a4_height_in))
    plt.subplots_adjust(left=0, right=0.8, bottom=0.2, top=0.9, wspace=0.4, hspace=0.4)

    # Set map bounds according to scale
    ax.set_aspect('equal')
    ax.set_xlim(center_x - plot_width / 2, center_x + plot_width / 2)
    ax.set_ylim(center_y - plot_height / 1.5, center_y + plot_height / 2)

    # Plot the map
    data2.plot(ax=ax, color="none", edgecolor='black')
    tao.plot(ax=ax,color='brown')

    for idx, row in tao.iterrows():
        if row.geometry.is_empty:
            continue 
        else: 
            ax.annotate(
                text=row['TOWN'],  
                xy=(row.geometry.x, row.geometry.y), 
                xytext=(1, 1), 
                textcoords="offset points",
                fontsize=6,
                color="black",
                ha='left',  # Horizontal alignment
                va='bottom'  # Vertical alignment
            )

    # Add title and grid
    size = "A4"
    ax.set_title(f'map of {selected_county} and its Towns Scale 1:{best_scale} {size}')

    ax.grid(True, color='blue', linestyle='--', linewidth=0.7)
    # Get gridline positions
    xticks = ax.get_xticks()  # X-axis gridline positions
    yticks = ax.get_yticks()  # Y-axis gridline positions


    # Turn off default axis tick labels
    ax.set_xticklabels([])  # Remove default x-axis tick labels
    ax.set_yticklabels([])  # Remove default y-axis tick labels

    x_min, x_max = ax.get_xlim()  # Visible x-axis range
    y_min, y_max = ax.get_ylim()  # Visible y-axis range

    # Get gridline positions
    xticks = ax.get_xticks()  # X-axis gridline positions
    yticks = ax.get_yticks()  # Y-axis gridline positions

    # Label only the x-axis gridlines within the visible range
    for xtick in xticks:
        if x_min <= xtick <= x_max:  # Only label gridlines within the visible x-range
            ax.text(xtick, y_min-(best_scale*0.1),  # Place label on the lower boundary of the map
                    f'{xtick:.1f}', color='black', fontsize=7,
                    ha='center', va='top')

    # Label only the y-axis gridlines within the visible range
    for ytick in yticks:
        if y_min <= ytick <= y_max:  # Only label gridlines within the visible y-range
            ax.text(x_min, ytick,  # Place label on the left boundary of the map
                    f'{ytick:.1f}', color='black', fontsize=7,
                    ha='right', va='center', rotation=90)  # Vertical label orientation

    # Add titles and labels 
    def text1(x1=1.04,x=0,text="hello",font=7):
        fig.text(x1, x, text, fontsize=font, color="black", transform=ax.transAxes, ha="left")


    text1(1.12,0.8,text4,9)
    text1(1.12,0.76,text5,7)
    text1(1.12,0.68,text6,7)
    text1(1.12,0.64,text7,9)
    text1(1.12,0.5,text8,9)
    text1(1.12,0.5,text9,7)
    text1(1.12,0.45,text10,14)
    text1(1.12,0.42,text11,7)
    import pandas as pd
    date=pd.Timestamp.today().strftime('%d-%m-%Y')
    name="Kipyegon Amos"
    text12=f" Scale :   {scale}\n \nDate:   {date}\n \nPrepared by:   {name}\n \nDrawn by:   Machine"
    text1(1.28,0.29,text12,6)
    text1(1.12,0.266,text13,6)
    text1(1.12,0.237,text14,9)
    text1(1.12,0.2,text15a,5)
    text1(1.12,0.175,text15,5)

    text1(1.12,0.14,text16,6)
    text1(1.12,0.09,text16a,5)
    text1(1.12,0.05,text17,5)
    text1(1.12,0.01,text18,8)



    bbox_props = dict(facecolor="white", edgecolor="red", boxstyle="round,pad=0.3", alpha=0.7)
    plt.text(1.05, 0.55, "", transform=ax.transAxes, bbox=bbox_props)
    def rect(x,y,width,height,color='black'):
        # x, y = 1.03, 0  # bottom-left corner coordinates
        # width, height = 0.4, 1  # rectangle dimensions

        # Create and add the rectangle patch
        rect = patches.Rectangle(
            (x, y), width, height,
            linewidth=1, edgecolor=color, facecolor="none", transform=ax.transAxes
        )
        return fig.patches.append(rect)
    rect(1.11,0,0.38,1)
    rect(1.14,0.9,0.1,0.05)
    rect(-0.03,-0.06,1.54,1.11,'red')

    def lined(x,x1,y,y1):

        underline = plt.Line2D([x, x1],
                            [y, y1],
                            transform=fig.transFigure,
                            color="black",
                            linewidth=1)
        fig.lines.append(underline)
    # plt.tight_layout()

    lined(0.77, 0.99,0.8,0.8)
    lined(0.77, 0.99,0.644,0.644)
    lined(0.84, 0.84,0.61,0.644)
    lined(0.77, 0.99,0.61,0.61)
    lined(0.77, 0.99,0.54,0.54)


    lined(0.77, 0.99,0.51,0.51)
    lined(0.77, 0.99,0.49,0.49)
    lined(0.85, 0.85,0.4,0.49)
    lined(0.77, 0.99,0.4,0.4)

    lined(0.77, 0.99,0.38,0.38)
    lined(0.77, 0.99,0.31,0.31)
    lined(0.77, 0.99,0.23,0.23)

    


    arrow_x, arrow_y = 1.164, 0.38
    plt.annotate(
                'N', 
                xy=(arrow_x, arrow_y), 
                xytext=(arrow_x, arrow_y - 0.08), 
                arrowprops=dict(facecolor='white', width=7, headwidth=20),
                ha='center', va='center', fontsize=10, color='black', xycoords='axes fraction'
            )
    import matplotlib.image as mpimg



        # Add image as inset (e.g., logo)
    img = mpimg.imread('amos.png')
    inset_ax = ax.inset_axes([0, 0.94, 0.1, 0.1])  # x, y, width, height in relative coords
    inset_ax.imshow(img)
    inset_ax.axis('off')





    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return f"data:image/png;base64,{encoded}",geojson,geojson1,center




server = app.server

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080
    app.run(debug=False, host="0.0.0.0", port=port)
