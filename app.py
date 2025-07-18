from dash import Dash, html,dash_table,dcc,callback,Output, Input,State
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import geopandas as gpd
import os
import dash_bootstrap_components as dbc
import io
import dash_leaflet as dl
import json
import simplekml
import dash



import base64


def gdf_to_kmz(gdf, kmz_path, name_field=None):
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError("Input must be a GeoDataFrame")

    if not all(gdf.geometry.geom_type == "Point"):
        raise ValueError("This function supports only Point geometries")

    if name_field and name_field not in gdf.columns:
        raise ValueError(f"'{name_field}' not found in the GeoDataFrame")

    kml = simplekml.Kml()
    for _, row in gdf.iterrows():
        geom = row.geometry
        name = str(row[name_field]) if name_field else "Point"
        kml.newpoint(name=name, coords=[(geom.x, geom.y)])

    kml.savekmz(kmz_path)
    print(f"✅ KMZ saved to: {kmz_path}")


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "geo dashboard"

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
    dbc.Row([
        dbc.Col([
   

    html.Div(children="Geo-Automation and Dashboard",className="title1")])]),
    
    dbc.Row([
        dbc.Col(html.Label("Choose the county to plot", style={'textAlign': 'center', 'color': 'red', 'fontSize': 30}), width=5),
        
    dbc.Col([
        dcc.Upload(
            id='upload-geo-file',
            children=html.Div(['Drag and Drop or ', html.A('Select a Geospatial File(zipped shp or GeoPackage)')],className="app-header"),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        html.Div(id='upload-feedback')
    ], width=6)
], justify="center"),

    
    dbc.Row([
        dbc.Col(dcc.Dropdown(options=data1['NAME_2'].unique(), value="Nairobi", id="counties", style={'width': '100%'}), width=5)
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(html.Img(id='plot', style={'width': '100%', 'height': 'auto'}), width=11)
    ],justify="center"),

    html.Br(),
    dbc.Row([
        dcc.Loading(
        id="loading",
        type="circle",
        children=[
            html.Div(id="content")
        ] 
    ),
  
    ],justify="center"),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=px.histogram(dat, x='NAME_2', y='TOWN'), style={'width': '100%'}), width=10,align="center")
    ],justify="center"),
     html.Br(),

   dbc.Row([
        dbc.Col(dl.Map([
            dl.TileLayer(),
            dl.GeoJSON(id="geojson", format="geojson", options=dict(
                style={
                    'fillColor': 'blue',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.6
                }
            )),
            dl.GeoJSON(id="geojson1", format="geojson", options=dict(
                style={
                    'fillColor': 'red',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.6
                }
            ))
        ],
        id="leaflet-map",
        center=[0, 0],
        zoom=9,
        style={"height": "70vh", "width": "100%", 'textAlign': 'center'}), width=10,
            align="center")
    ], justify="center"),

    html.Br(),
    dbc.Row([
        dbc.Col(html.Div(children="Let's take Geospatial and Survey to a new level", style={'textAlign': 'center', 'color': 'red', 'fontSize': 20}), width=12)
    ]),

    html.Br(),

    dbc.Row([
            html.H2("Ganerate Kmz here(upload csv)", className="text-center mt-3 mb-4"),

    dcc.Upload(
        id='upload-data',
        children=html.Div(['📁 Drag and Drop or ', html.A('Select a CSV File')]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed',
            'borderRadius': '5px', 'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
         dbc.Col([

            dbc.Label("X column:"),
            dcc.Dropdown(id='x-column')
        ], width=2),
        dbc.Col([
            dbc.Label("Y column:"),
            dcc.Dropdown(id='y-column')
        ], width=2),
           dbc.Col([
            dbc.Label("Label column:"),
            dcc.Dropdown(id='label-column')
        ], width=2),

    ]),
    dbc.Row([
        dbc.Button("Download Filtered KMZ", id="download-kmz-btn", color="success", className="mb-3"),
        dcc.Download(id="download-kmz"),
        dcc.Store(id='filtered-data')
    ]),
   
  dbc.Row([
    dbc.Col(
        html.A("Connect with me; My Portfolio", 
               href="https://kipyegon2000.github.io/amos-portfolio/", 
               target="_blank", 
               style={
                   "fontWeight": "bold",
                   "textAlign": "center",
                   "display": "block",
                   'fontSize': 30
                  

               }),
        width="auto", className="mx-auto"
    )
]),
 dbc.Row([
        dbc.Col(html.H3("Created By Kipyegon Amos", style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30}), width=12, className="text-center",align="center")
    ], className="mt-3"),
    
    dcc.Store(id='geojson-store'),
    dcc.Store(id='geojson-bounds'),
    dcc.Store(id='base-bounds'),
], fluid=True)


import tempfile
@app.callback(
    Output('geojson-store', 'data'),
    Output('geojson-bounds', 'data'),
    Output('base-bounds', 'data'),
    Output('upload-feedback', 'children'),
    Input('upload-geo-file', 'contents'),
    State('upload-geo-file', 'filename'),
)
def handle_geo_upload(contents, filename):
    if contents is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        tmp.write(decoded)
        temp_path = tmp.name

    try:
        gdf = gpd.read_file(temp_path)
        gdf = gdf.to_crs(epsg=21037)
        base_bound = gdf.to_crs(epsg=4326)
        base_bound = list(base_bound.total_bounds)
        bound = list(gdf.total_bounds)
        json_data = json.loads(gdf.to_json())
        return json_data, bound, base_bound, f"✅ Uploaded: {filename}"
    except Exception as e:
        return dash.no_update, dash.no_update, dash.no_update, f"❌ Error reading file: {e}"
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

@callback(
    Output(component_id='plot', component_property='src'),
    Output(component_id="geojson", component_property="data"),
    Output(component_id="geojson1", component_property="data"),
    Output(component_id="leaflet-map", component_property="center"),
    Input(component_id='counties', component_property='value'),
    Input(component_id='geojson-store', component_property='data'),
    Input(component_id="geojson-bounds", component_property="data"),
    Input(component_id="base-bounds", component_property="data"),
)
def update_image(selected_county, uploaded_geojson, bound, base_bound):
    if uploaded_geojson:
        # Process uploaded data
        data2 = gpd.GeoDataFrame.from_features(uploaded_geojson['features'])
        data2.crs = "EPSG:21037"  # Ensure CRS is set
        geojson = data2.to_crs(epsg=4326)
        geojson_data = json.loads(geojson.to_json())
        bounds = base_bound
        bou = bound
        selected_county="study area"
        
        # For points, use point style; for polygons, use polygon style
        if all(geom.type in ['Point', 'MultiPoint'] for geom in data2.geometry):
            geojson1 = None  # No secondary data for points
        else:
            geojson1 = geojson_data  # Use same data for polygons
    else:
        # Process county data
        data2 = data1[data1['NAME_2'] == selected_county]
        data3 = data2.unary_union
        da = data2.to_crs(epsg=4326)
        geojson_data = json.loads(da.to_json())
        bounds = da.total_bounds
        bou = data2.total_bounds
        tao = town[town.geometry.within(data3)]
        ta = tao.to_crs(epsg=4326)
        geojson1 = json.loads(ta.to_json())

    # Calculate center for map
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2
    center = [center_lat, center_lon]
   

    minx, miny, maxx, maxy=bou 
    
    width, height = maxx - minx, maxy - miny
    
    map_width = maxx - minx  
    map_height = maxy - miny 

    a4_width_potrait, a4_height_potrait = 8.27, 11.69

    a4_width, a4_height =   11.69,8.27
    a4_width_in=a4_width
    a4_height_in=a4_height

    # Available scales
    scales = [100,500,1000, 2500, 5000, 10000, 25000, 50000,100000,250000,500000,1000000]

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
    if uploaded_geojson:
        pass

    else:
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

    
    ax.set_title(f'Map  of {selected_county} Scale 1:{best_scale}')

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
    img = mpimg.imread('assets/amos.png')
    inset_ax = ax.inset_axes([0, 0.94, 0.1, 0.1])  # x, y, width, height in relative coords
    inset_ax.imshow(img)
    inset_ax.axis('off')





    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return f"data:image/png;base64,{encoded}", geojson_data, geojson1, center


@app.callback(
   
   
    Output('x-column', 'options'),
    Output('y-column', 'options'),
    Output('filtered-data', 'data'),
    Output('label-column', 'options'),
    
  
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
)
def handle_upload(contents, filename):
    if contents is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
   
    all_cols = df.columns.tolist()
    options = [{'label': col, 'value': col} for col in all_cols]
    cat_cols = df.select_dtypes(include='object').columns.tolist()
    cat_options = [{'label': col, 'value': col} for col in cat_cols]

  

    return  options, options,df.to_dict('records'),cat_options

@app.callback(
       
       
    Output("download-kmz", "data"),

    Input("download-kmz-btn", "n_clicks"),
    State("filtered-data", "data"),
    State("x-column", "value"),
    State("y-column", "value"),
     State("label-column", "value"),
 

    prevent_initial_call=True
)
def download_kmz(n_clicks, data,x_col, y_col,label_col ):
    df1 = pd.DataFrame(data)
    

    gdf = gpd.GeoDataFrame(df1, geometry=gpd.points_from_xy(df1[x_col], df1[y_col]), crs="EPSG:4326")
    kmz_path = "filtered_output.kmz"
    gdf_to_kmz(gdf, kmz_path, name_field=label_col)

    with open(kmz_path, "rb") as f:
        content = f.read()
    encoded = base64.b64encode(content).decode()
    os.remove(kmz_path)

    return dict(content=encoded, filename="filtered_data.kmz", base64=True)


server = app.server

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080
    app.run(debug=False, host="0.0.0.0", port=port)
