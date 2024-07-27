import pandas as pd
import folium
#import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static
import streamlit.components.v1 as components
import requests
from io import BytesIO

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded")

@st.cache_data
def load_data(url):
    response = requests.get(url)
    response.raise_for_status()  # Kiểm tra xem có lỗi khi tải file không
    data = pd.read_excel(BytesIO(response.content), engine='openpyxl')
    return data

# Sử dụng URL dạng thô để tải file Excel từ GitHub
file_path_data = "https://raw.githubusercontent.com/thuthuy119/agricultural_products/main/TradeData_DriedMango_processed.xlsx"
data = load_data(file_path_data)

# Lấy các giá trị duy nhất trong cột "Product"
product_options = data['Product'].unique()

# Sử dụng Streamlit để tạo Navigation panel
st.sidebar.title('Navigation Panel')
selected_product = st.sidebar.radio("Chọn sản phẩm", product_options)
st.markdown("<h2 style='font-weight: bold;text-align: center; color:firebrick;'> PHÂN TÍCH TÌNH HÌNH XUẤT NHẬP KHẨU MỘT SỐ SẢN PHẨM NÔNG SẢN TẠI VIỆT NAM (THÁNG 7/2023 - THÁNG 7/2024)</h2>", unsafe_allow_html=True)

with st.expander("PHẦN 1 - PHÂN TÍCH TOÀN THỊ TRƯỜNG"):
    # Sử dụng st.markdown để chèn HTML
    st.markdown("<h3 style='font-weight: bold;color:#AD2A1A;'>Phân tích tổng quan về thị trường</h3>", unsafe_allow_html=True)

    # Sử dụng st.markdown để chèn HTML
    st.markdown("<h5 style='font-weight: bold;color:#AD2A1A;'>Số lượng giao dịch</h5>", unsafe_allow_html=True)

    # Đếm số lượng giao dịch theo từng tháng/năm và loại Import/Export
    transaction_counts = data.groupby(['Month/Year', 'Import/Export']).size().unstack(fill_value=0).reset_index()

    # Chuyển đổi cột 'Month/Year' thành chuỗi để Plotly có thể xử lý
    transaction_counts['Month/Year'] = transaction_counts['Month/Year'].astype(str)

    # Tính tỷ lệ thay đổi theo tháng cho Import và Export
    transaction_counts['Import Ring Ratio'] = transaction_counts['Import'].pct_change() * 100
    transaction_counts['Export Ring Ratio'] = transaction_counts['Export'].pct_change() * 100

    # Làm tròn đến 1 chữ số sau dấu phẩy
    transaction_counts['Import Ring Ratio'] = transaction_counts['Import Ring Ratio'].round(1)
    transaction_counts['Export Ring Ratio'] = transaction_counts['Export Ring Ratio'].round(1)

    # Vẽ biểu đồ dạng cột cụm bằng Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(x=transaction_counts['Month/Year'], y=transaction_counts['Import'], name='Import', marker_color='rgb(31, 119, 180)'))
    fig.add_trace(go.Bar(x=transaction_counts['Month/Year'], y=transaction_counts['Export'], name='Export', marker_color='rgb(255, 127, 14)'))
   
    fig.add_trace(go.Scatter(x=transaction_counts['Month/Year'], y=transaction_counts['Import Ring Ratio'], name='Import Ring Ratio', line=dict(color='rgb(255, 0, 0)', width=2), yaxis='y2'))
    fig.add_trace(go.Scatter(x=transaction_counts['Month/Year'], y=transaction_counts['Export Ring Ratio'], name='Export Ring Ratio', line=dict(color='rgb(0, 128, 0)', width=2), yaxis='y2'))
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        paper_bgcolor='rgb(252, 252, 252)',  
        plot_bgcolor='rgb(252, 252, 252)',   
        margin=dict(l=40, r=40, t=40, b=40)  
    )

    # Chuyển legend xuống dưới, ở giữa biểu đồ và bỏ tên của legend
    fig.update_layout(
        legend=dict(
            title_text='',
            orientation='h',
            yanchor='bottom',
            y=-0.3,
            xanchor='center',
            x=0.5
        ),
        xaxis=dict(title='Month/Year'),
        yaxis=dict(title='Tổng số lượng giao dịch', title_standoff=10, showgrid=True, gridcolor='rgba(0, 0, 0, 0)'),
        yaxis2=dict(title='Ring Ratio (%)', overlaying='y', side='right', tickformat='.1f', title_standoff=10, showgrid=True, gridcolor='rgba(0, 0, 0, 0)')
    )

    # Đồng bộ font chữ cho tất cả text trong biểu đồ
    fig.update_layout(
        font=dict(
            family="Arial",
            size=12,
            color="Black"
        )
    )

    # Hiển thị biểu đồ trên Streamlit
    #st.title("Market Analysis - Transactions")
    st.plotly_chart(fig, use_container_width=True)

    # Tính tổng số giao dịch nhập khẩu và xuất khẩu
    total_imports = data[data['Import/Export'] == 'Import'].shape[0]
    total_exports = data[data['Import/Export'] == 'Export'].shape[0]
    
    # Display the output in two columns
    col1, col2 = st.columns(2)
    # Hiển thị tổng số giao dịch nhập khẩu và xuất khẩu
    with col1:
        st.write("Tổng số giao dịch nhập khẩu:", total_imports)
    with col2:
        st.write("Tổng số giao dịch xuất khẩu:", total_exports)


    # Sử dụng st.markdown để chèn HTML
    st.markdown("<h5 style='font-weight: bold;color:#AD2A1A;'>Giá trị giao dịch</h5>", unsafe_allow_html=True)

    # Tính tổng giá trị giao dịch theo từng tháng/năm và loại Import/Export
    transaction_amounts = data.groupby(['Month/Year', 'Import/Export'])['Amount'].sum().unstack(fill_value=0).reset_index()

    # Chuyển đổi cột 'Month/Year' thành chuỗi để Plotly có thể xử lý
    transaction_amounts['Month/Year'] = transaction_amounts['Month/Year'].astype(str)

    # Tính tỷ lệ thay đổi theo tháng cho Export
    transaction_amounts['Export Ring Ratio'] = transaction_amounts['Export'].pct_change() * 100

    # Làm tròn đến 1 chữ số sau dấu phẩy
    transaction_amounts['Export Ring Ratio'] = transaction_amounts['Export Ring Ratio'].round(1)

    # Vẽ biểu đồ dạng cột cụm bằng Plotly
    fig = go.Figure()

    # Thêm các cột Import và Export
    fig.add_trace(go.Bar(x=transaction_amounts['Month/Year'], y=transaction_amounts['Import'], name='Import', marker_color='rgb(31, 119, 180)'))
    fig.add_trace(go.Bar(x=transaction_amounts['Month/Year'], y=transaction_amounts['Export'], name='Export', marker_color='rgb(255, 127, 14)'))

    # Thêm đường tỷ lệ thay đổi Export
    fig.add_trace(go.Scatter(x=transaction_amounts['Month/Year'], y=transaction_amounts['Export Ring Ratio'], name='Export Ring Ratio', line=dict(color='rgb(0, 128, 0)', width=2), yaxis='y2'))

    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        paper_bgcolor='rgb(252, 252, 252)',  
        plot_bgcolor='rgb(252, 252, 252)',   
        margin=dict(l=40, r=40, t=40, b=40)  
    )

    fig.update_layout(
        legend=dict(
            title_text='',
            orientation='h',
            yanchor='bottom',
            y=-0.3,
            xanchor='center',
            x=0.5
        ),
        xaxis=dict(title='Month/Year'),
        yaxis=dict(title='Giá trị giao dịch', title_standoff=10, showgrid=True, gridcolor='rgba(0, 0, 0, 0)'),
        yaxis2=dict(title='Ring Ratio (%)', overlaying='y', side='right', tickformat='.1f', title_standoff=10, showgrid=True, gridcolor='rgba(0, 0, 0, 0)')
    )

    fig.update_layout(
        font=dict(
            family="Arial",
            size=12,
            color="Black"
        )
    )

    # Hiển thị biểu đồ trên Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Tính tổng giá trị nhập khẩu và xuất khẩu
    total_import_value = data[data['Import/Export'] == 'Import']['Amount'].sum()
    total_export_value = data[data['Import/Export'] == 'Export']['Amount'].sum()

    # Hiển thị tổng giá trị  nhập khẩu và xuất khẩu
    # Display the output in two columns
    col1, col2 = st.columns(2)
    # Hiển thị tổng số giao dịch nhập khẩu và xuất khẩu
    with col1:
        st.write("Tổng giá trị nhập khẩu:", round(total_import_value, 2))
    with col2:
        st.write("Tổng giá trị xuất khẩu:", round(total_export_value, 2))

   
with st.expander("PHẦN 2 - PHÂN TÍCH THEO TỪNG QUỐC GIA"):
    # Tạo hộp chọn trong thanh bên để chọn giá trị trong cột "Import/Export"
    selected_value = st.selectbox('Chọn giá trị Import/Export', data['Import/Export'].unique())

    # Lọc dữ liệu dựa trên giá trị đã chọn
    filtered_data = data[data['Import/Export'] == selected_value]

    # Tính tổng giá trị (Amount) cho mỗi quốc gia
    amount_by_country = filtered_data.groupby('Destination')['Amount'].sum().reset_index()

    # Tạo bản đồ
    political_countries_url = "http://geojson.xyz/naturalearth-3.3.0/ne_50m_admin_0_countries.geojson"
    m = folium.Map(location=[25, 10], zoom_start=2, tiles="cartodb positron")

    choropleth = folium.Choropleth(
        geo_data=political_countries_url,
        data=amount_by_country,
        columns=["Destination", "Amount"],
        key_on="feature.properties.name",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color="white",
        legend_name=f"Tổng giá trị",
        name=f"Tổng giá trị {selected_value} của Việt Nam"
    ).add_to(m)

    # Tùy chỉnh thanh legend
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['name'], labels=True)
    )
    folium.LayerControl().add_to(m)

    # Render bản đồ Folium thành HTML
    map_html = m.get_root().render()

    # Hiển thị bản đồ trong ứng dụng Streamlit với chiều cao và chiều rộng tự động
    components.html(
        f"""
        <div style="width: 100%; height: 100vh;">
            {map_html}
        </div>
        """,
        height=650  # Đặt giá trị height đủ lớn để phần tử iframe có thể điều chỉnh kích thước
    )

    # Xác định loại giao dịch
    transaction_type = "nhập khẩu" if selected_value == "Export" else "xuất khẩu"

    # Chèn tiêu đề vào ứng dụng Streamlit
    st.markdown(f"<h5 style='font-weight: bold;color:#AD2A1A;'>Giá trị giao dịch của top 10 nước {transaction_type} lớn nhất của Việt Nam</h5>", unsafe_allow_html=True)
        
    # Tính tổng giá trị (Amount) cho mỗi quốc gia
    amount_by_country = filtered_data.groupby('Destination')['Amount'].sum().reset_index()

    # Lấy top 10 quốc gia có tổng giá trị lớn nhất
    top_10_countries = amount_by_country.nlargest(10, 'Amount')

    # Vẽ biểu đồ bằng Plotly
    fig = px.bar(top_10_countries, x='Amount', y='Destination', orientation='h',
                labels={'Amount': '', 'Destination': ''},
                color='Amount', color_continuous_scale=px.colors.sequential.Viridis_r)

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        paper_bgcolor='rgb(252, 252, 252)', 
        plot_bgcolor='rgb(252, 252, 252)',   
        margin=dict(l=40, r=40, t=40, b=40)  
    )

    # Hiển thị biểu đồ trong ứng dụng Streamlit
    st.plotly_chart(fig, use_container_width=True)

        # Chèn tiêu đề vào ứng dụng Streamlit
    st.markdown(f"<h5 style='font-weight: bold;color:#AD2A1A;'>Giá trị xuất/nhập khẩu theo quốc gia</h5>", unsafe_allow_html=True)


    # Tạo danh sách các quốc gia duy nhất từ cột "Destination"
    countries = data['Destination'].unique()

    # Tạo một selectbox để chọn quốc gia
    selected_country = st.selectbox('Chọn quốc gia', countries)

    # Lọc dữ liệu cho quốc gia được chọn
    country_data = data[data['Destination'] == selected_country]

    # Kiểm tra nếu không có dữ liệu cho quốc gia này
    if country_data.empty:
        st.write(f"Không có dữ liệu cho quốc gia {selected_country}")
    else:
        # Thêm cột Month/Year để nhóm dữ liệu
        country_data['Month/Year'] = country_data['Date'].dt.to_period('M')

        # Tính tổng giá trị  theo từng tháng/năm và loại Import/Export
        transaction_values = country_data.groupby(['Month/Year', 'Import/Export'])['Amount'].sum().unstack(fill_value=0).reset_index()

        # Chuyển đổi cột 'Month/Year' thành chuỗi để Plotly có thể xử lý
        transaction_values['Month/Year'] = transaction_values['Month/Year'].astype(str)

        # In ra tổng giá trị của Import/Export
        if 'Import' in transaction_values.columns:
            total_import_value = transaction_values['Import'].sum()
            st.write(f"Tổng giá trị nhập khẩu của Việt Nam:", round(total_import_value, 2))
        else:
            total_import_value = 0
            st.write("Không có dữ liệu Việt Nam nhập khẩu từ nước này")

        if 'Export' in transaction_values.columns:
            total_export_value = transaction_values['Export'].sum()
            st.write(f"Tổng giá trị xuất khẩu từ Việt Nam:", round(total_export_value, 2))
        else:
            total_export_value = 0
            st.write("Không có dữ liệu Việt Nam xuất khẩu sang nước này")

        # Tính tỷ lệ thay đổi theo tháng cho Import và Export nếu tồn tại
        if 'Import' in transaction_values.columns:
            transaction_values['Import Ring Ratio'] = transaction_values['Import'].pct_change() * 100
            transaction_values['Import Ring Ratio'] = transaction_values['Import Ring Ratio'].round(1)
        else:
            transaction_values['Import'] = 0
            transaction_values['Import Ring Ratio'] = 0

        if 'Export' in transaction_values.columns:
            transaction_values['Export Ring Ratio'] = transaction_values['Export'].pct_change() * 100
            transaction_values['Export Ring Ratio'] = transaction_values['Export Ring Ratio'].round(1)
        else:
            transaction_values['Export'] = 0
            transaction_values['Export Ring Ratio'] = 0

        # Vẽ biểu đồ dạng cột cụm bằng Plotly
        fig = go.Figure()

        # Thêm các cột Import và Export nếu tồn tại dữ liệu
        if transaction_values['Import'].sum() > 0:
            fig.add_trace(go.Bar(x=transaction_values['Month/Year'], y=transaction_values['Import'], name='Import', marker_color='rgb(31, 119, 180)'))
        if transaction_values['Export'].sum() > 0:
            fig.add_trace(go.Bar(x=transaction_values['Month/Year'], y=transaction_values['Export'], name='Export', marker_color='rgb(255, 127, 14)'))

        # Thêm các đường tỷ lệ thay đổi Import và Export nếu tồn tại dữ liệu
        if transaction_values['Import Ring Ratio'].sum() > 0:
            fig.add_trace(go.Scatter(x=transaction_values['Month/Year'], y=transaction_values['Import Ring Ratio'], name='Import Ring Ratio', line=dict(color='rgb(255, 0, 0)', width=2), yaxis='y2'))
        if transaction_values['Export Ring Ratio'].sum() > 0:
            fig.add_trace(go.Scatter(x=transaction_values['Month/Year'], y=transaction_values['Export Ring Ratio'], name='Export Ring Ratio', line=dict(color='rgb(0, 128, 0)', width=2), yaxis='y2'))

        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            paper_bgcolor='rgb(252, 252, 252)', 
            plot_bgcolor='rgb(252, 252, 252)',   
            margin=dict(l=40, r=40, t=40, b=40)  
        )

        fig.update_layout(
            legend=dict(
                title_text='',
                orientation='h',
                yanchor='bottom',
                y=-0.2,
                xanchor='center',
                x=0.5
            ),
            xaxis=dict(title='Month/Year'),
            yaxis=dict(title='Tổng giá trị giao dịch', title_standoff=10, showgrid=True, gridcolor='rgba(0, 0, 0, 0)'),
            yaxis2=dict(title='Ring Ratio (%)', overlaying='y', side='right', tickformat='.1f', title_standoff=10, showgrid=True, gridcolor='rgba(0, 0, 0, 0)')
        )
        # Hiển thị biểu đồ
        st.plotly_chart(fig, use_container_width=True)


with st.expander("PHẦN 3 - PHÂN TÍCH THEO NHÀ NHẬP KHẨU/NHÀ XUẤT KHẨU"):

    # Tạo selection bar với hai giá trị "Xuất khẩu" và "Nhập khẩu"
    selection = st.selectbox('Chọn loại giao dịch', ['Việt Nam xuất khẩu đến các nước khác', 'Việt Nam nhập khẩu từ các nước khác'])

    #hàm vẽ biểu đồ 
    def plot_top_20_with_hover(data, import_export, role, title, hover_column):
        # Lọc dữ liệu theo Import/Export
        filtered_data = data[data['Import/Export'] == import_export]
        
        # Tính tổng giá trị (Amount) cho mỗi Purchaser hoặc Supplier và lấy thêm cột Country
        if role == 'Purchaser':
            grouped_data = filtered_data.groupby([role, hover_column])['Amount'].sum().reset_index()
        elif role == 'Supplier':
            grouped_data = filtered_data.groupby([role, hover_column])['Amount'].sum().reset_index()

        # Lấy top 20 Purchasers hoặc Suppliers có tổng giá trị lớn nhất
        top_20 = grouped_data.nlargest(20, 'Amount')

        # Vẽ biểu đồ bằng Plotly
        fig = px.bar(top_20, x='Amount', y=role, orientation='h',
                    labels={'Amount': '', role: ''},
                    color='Amount', color_continuous_scale=px.colors.sequential.Viridis_r,
                    hover_data={hover_column: True, 'Amount': True})

        # Đổi tên các cột trong hover data và làm tròn Amount
        fig.update_traces(hovertemplate='<b>%{y}</b><br>Giá trị: %{x:.2f}<br>' + hover_column + ': %{customdata[0]}<extra></extra>')

        # Cập nhật nền thành màu xám cực nhạt
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            paper_bgcolor='rgb(252, 252, 252)',  # Màu xám cực nhạt
            plot_bgcolor='rgb(252, 252, 252)',   # Màu xám cực nhạt
            margin=dict(l=40, r=40, t=40, b=40),  # Thu hẹp phần nền lại
            #title=title
        )

        # Hiển thị biểu đồ trong Streamlit
        st.plotly_chart(fig, use_container_width=True)

    if selection == 'Việt Nam xuất khẩu đến các nước khác':
        
        st.markdown("<h5 style='font-weight: bold;color:#AD2A1A;'>Tổng số lượng nhà nhập khẩu </h5>", unsafe_allow_html=True)

        # Chọn dữ liệu Export
        export_data = data[data['Import/Export'] == 'Export']

        # Đếm số lượng nhà cung cấp (unique)
        unique_suppliers_count = export_data['Purchaser'].nunique()

        # Hiển thị giá trị đó thông qua st.write
        st.write('Tổng số lượng nhà nhập khẩu:', unique_suppliers_count)

        # Group by Month/Year and count unique Purchasers for Export
        export_purchasers = export_data.groupby('Month/Year')['Purchaser'].nunique().reset_index()

        # Calculate ring ratio for Export Purchasers
        export_purchasers['Ring Ratio'] = export_purchasers['Purchaser'].pct_change() * 100
        export_purchasers['Ring Ratio'] = export_purchasers['Ring Ratio'].round(1)

        # Chuyển đổi cột 'Month/Year' thành chuỗi để Plotly có thể xử lý
        export_purchasers['Month/Year'] = export_purchasers['Month/Year'].astype(str)

        # Plot for Export Purchasers
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=export_purchasers['Month/Year'], y=export_purchasers['Purchaser'], name='Số lượng nhà nhập khẩu', marker_color='rgb(31, 119, 180)'))
        fig1.add_trace(go.Scatter(x=export_purchasers['Month/Year'], y=export_purchasers['Ring Ratio'], name='Ring Ratio', line=dict(color='rgb(255, 0, 0)', width=2), yaxis='y2'))

        fig1.update_layout(
            yaxis=dict(title='Số lượng nhà nhập khẩu', showgrid=False),
            paper_bgcolor='rgb(252, 252, 252)', 
            plot_bgcolor='rgb(252, 252, 252)',   
            margin=dict(l=40, r=40, t=40, b=40),  # Thu hẹp phần nền lại
            legend=dict(
                title_text='',
                orientation='h',
                yanchor='bottom',
                y=-0.3,
                xanchor='center',
                x=0.5
            ),
            xaxis=dict(title='Month/Year', showgrid=False),
            yaxis2=dict(title='Ring Ratio (%)', overlaying='y', side='right', tickformat='.1f', showgrid=False)
        )

        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("<h5 style='font-weight: bold;color:#AD2A1A;'>Top 20 nhà nhập khẩu lớn nhất </h5>", unsafe_allow_html=True)

        plot_top_20_with_hover(data, 'Export', 'Purchaser', 'Top 20 Purchasers by Total Amount (Export)', 'Destination')

        
        st.markdown("<h5 style='font-weight: bold;color:#AD2A1A;'>Tổng số lượng nhà xuất khẩu </h5>", unsafe_allow_html=True)
        # Đếm số lượng nhà cung cấp (unique)
        unique_suppliers_count = export_data['Supplier'].nunique()

        # Hiển thị giá trị đó thông qua st.write
        st.write('Tổng số lượng nhà xuất khẩu:', unique_suppliers_count)
        export_suppliers_vn = export_data.groupby('Month/Year')['Supplier'].nunique().reset_index()

        # Calculate ring ratio for Export Suppliers in Vietnam
        export_suppliers_vn['Ring Ratio'] = export_suppliers_vn['Supplier'].pct_change() * 100
        export_suppliers_vn['Ring Ratio'] = export_suppliers_vn['Ring Ratio'].round(1)

        # Chuyển đổi cột 'Month/Year' thành chuỗi để Plotly có thể xử lý
        export_suppliers_vn['Month/Year'] = export_suppliers_vn['Month/Year'].astype(str)

        # Plot for Export Suppliers in Vietnam
        fig = go.Figure()
        fig.add_trace(go.Bar(x=export_suppliers_vn['Month/Year'], y=export_suppliers_vn['Supplier'], name='Số lượng nhà xuất khẩu', marker_color='rgb(31, 119, 180)'))
        fig.add_trace(go.Scatter(x=export_suppliers_vn['Month/Year'], y=export_suppliers_vn['Ring Ratio'], name='Ring Ratio', line=dict(color='rgb(255, 0, 0)', width=2), yaxis='y2'))

        fig.update_layout(
            yaxis=dict(title='số lượng nhà xuất khẩu', showgrid=False),
            paper_bgcolor='rgb(252, 252, 252)', 
            plot_bgcolor='rgb(252, 252, 252)',   
            margin=dict(l=40, r=40, t=40, b=40),  # Thu hẹp phần nền lại
            legend=dict(
                title_text='',
                orientation='h',
                yanchor='bottom',
                y=-0.3,
                xanchor='center',
                x=0.5
            ),
            xaxis=dict(title='Month/Year', showgrid=False),
            yaxis2=dict(title='Ring Ratio (%)', overlaying='y', side='right', tickformat='.1f', showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<h5 style='font-weight: bold;color:#AD2A1A;'>Top 20 nhà xuất khẩu lớn nhất </h5>", unsafe_allow_html=True)

        plot_top_20_with_hover(data, 'Export', 'Supplier', 'Top 20 Purchasers by Total Amount (Export)', 'Destination')

    elif selection == 'Việt Nam nhập khẩu từ các nước khác':
        
        st.markdown("<h5 style='font-weight: bold;color:#AD2A1A;'>Tổng số lượng nhà xuất khẩu </h5>", unsafe_allow_html=True)

        # Chọn dữ liệu Import
        import_data = data[data['Import/Export'] == 'Import']

        # Đếm số lượng nhà cung cấp (unique)
        unique_suppliers_count = import_data['Supplier'].nunique()

        # Hiển thị giá trị đó thông qua st.write
        st.write('Tổng số lượng nhà xuất khẩu:', unique_suppliers_count)

        # Group by Month/Year and count unique Suppliers for Import
        import_suppliers = import_data.groupby('Month/Year')['Supplier'].nunique().reset_index()

        # Calculate ring ratio for Import Suppliers
        import_suppliers['Ring Ratio'] = import_suppliers['Supplier'].pct_change()

        # Calculate ring ratio for Import Suppliers
        import_suppliers['Ring Ratio'] = import_suppliers['Supplier'].pct_change() * 100
        import_suppliers['Ring Ratio'] = import_suppliers['Ring Ratio'].round(1)

        # Chuyển đổi cột 'Month/Year' thành chuỗi để Plotly có thể xử lý
        import_suppliers['Month/Year'] = import_suppliers['Month/Year'].astype(str)

        # Plot for Import Suppliers
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=import_suppliers['Month/Year'], y=import_suppliers['Supplier'], name='Số lượng nhà xuất khẩu', marker_color='rgb(31, 119, 180)'))
        fig1.add_trace(go.Scatter(x=import_suppliers['Month/Year'], y=import_suppliers['Ring Ratio'], name='Ring Ratio', line=dict(color='rgb(255, 0, 0)', width=2), yaxis='y2'))

        fig1.update_layout(
            yaxis=dict(title='Số lượng nhà xuất khẩu', showgrid=False),
            paper_bgcolor='rgb(252, 252, 252)', 
            plot_bgcolor='rgb(252, 252, 252)',   
            margin=dict(l=40, r=40, t=40, b=40),  # Thu hẹp phần nền lại
            legend=dict(
                title_text='',
                orientation='h',
                yanchor='bottom',
                y=-0.3,
                xanchor='center',
                x=0.5
            ),
            xaxis=dict(title='Month/Year', showgrid=False),
            yaxis2=dict(title='Ring Ratio (%)', overlaying='y', side='right', tickformat='.1f', showgrid=False)
        )

        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("<h5 style='font-weight: bold;color:#AD2A1A;'>Top 20 nhà xuất khẩu lớn nhất </h5>", unsafe_allow_html=True)

        plot_top_20_with_hover(data, 'Import', 'Supplier', 'Top 20 Suppliers by Total Amount (Import)', 'Destination')

        st.markdown("<h5 style='font-weight: bold;color:#AD2A1A;'>Tổng số lượng nhà nhập khẩu </h5>", unsafe_allow_html=True)
        
        # Đếm số lượng nhà nhập khẩu (unique)
        unique_purchasers_count = import_data['Purchaser'].nunique()

        # Hiển thị giá trị đó thông qua st.write
        st.write('Tổng số lượng nhà nhập khẩu:', unique_purchasers_count)

        import_purchasers = import_data.groupby('Month/Year')['Purchaser'].nunique().reset_index()

        # Calculate ring ratio for Import Purchasers
        import_purchasers['Ring Ratio'] = import_purchasers['Purchaser'].pct_change() * 100
        import_purchasers['Ring Ratio'] = import_purchasers['Ring Ratio'].round(1)

        # Chuyển đổi cột 'Month/Year' thành chuỗi để Plotly có thể xử lý
        import_purchasers['Month/Year'] = import_purchasers['Month/Year'].astype(str)

        # Plot for Import Purchasers
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=import_purchasers['Month/Year'], y=import_purchasers['Purchaser'], name='Số lượng nhà nhập khẩu', marker_color='rgb(31, 119, 180)'))
        fig2.add_trace(go.Scatter(x=import_purchasers['Month/Year'], y=import_purchasers['Ring Ratio'], name='Ring Ratio', line=dict(color='rgb(255, 0, 0)', width=2), yaxis='y2'))

        fig2.update_layout(
            yaxis=dict(title='Số lượng nhà nhập khẩu', showgrid=False),
            paper_bgcolor='rgb(252, 252, 252)', 
            plot_bgcolor='rgb(252, 252, 252)',   
            margin=dict(l=40, r=40, t=40, b=40),  # Thu hẹp phần nền lại
            legend=dict(
                title_text='',
                orientation='h',
                yanchor='bottom',
                y=-0.3,
                xanchor='center',
                x=0.5
            ),
            xaxis=dict(title='Month/Year', showgrid=False),
            yaxis2=dict(title='Ring Ratio (%)', overlaying='y', side='right', tickformat='.1f', showgrid=False)
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<h5 style='font-weight: bold;color:#AD2A1A;'>Top 20 nhà nhập khẩu lớn nhất </h5>", unsafe_allow_html=True)

        plot_top_20_with_hover(data, 'Import', 'Purchaser', 'Top 20 Purchasers by Total Amount (Import)', 'Destination')


    #st.plotly_chart(fig, use_container_width=True)
