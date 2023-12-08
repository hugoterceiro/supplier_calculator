import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.graph_objects as go

st.set_page_config(layout="centered")

with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)


def get_main_inputs():

    col1, col2 =  st.columns(2, gap="medium")

    with col1:
        client_base = st.number_input("Número de clientes", min_value = 0,help="Número de clientes ativos transacionando por mês.",value=3000)
        acquitisions_per_month = st.number_input("Novos clientes por mês", min_value = 0,help ="Número de novos clientes ativos por mês.", value=30)
         

    with col2:
        average_monthly_spend = st.number_input("Spending médio mensal, em R$", min_value = 0.0, help ="Média de gastos por cliente no mês.",value=1000.0, format="%f", step=100.)
        creditless_base = st.number_input("Clientes sem crédito", min_value = 0,help="Número de clientes ativos que não possuem uma forma de crédito para pagamento.", value=200)
        

    payment_term = st.selectbox("Prazo desejado", help="Número máximo de dias para repasse das compras do cliente para você.", options=[30, 60, 90])
    liquid_margins = st.slider("Margem Líquida", help="Divisão do lucro líquido pela receita líquida.", min_value=-1.0, max_value=10.0, step=0.1, value=3., format="%f %%")

    return {
        "client_base": client_base,
        "average_monthly_spend": average_monthly_spend,
        "liquid_margins": liquid_margins,
        "acquitisions_per_month": acquitisions_per_month,
        "creditless_base": creditless_base,
        "payment_term": payment_term
    }


def get_model_parameters():

    # left, right =  st.columns(2, gap="medium")

    # with left:
    #     fee_30 = st.slider("Taxa para prazo 60 dias", min_value=-1.0, max_value=10.0, step=0.1, value=3., format="%f %%")
    #     fee_60 = st.slider("Taxa para prazo 60 dias", min_value=-1.0, max_value=10.0, step=0.1, value=3.8, format="%f %%")
    #     fee_90 = st.slider("Taxa para prazo 90 dias", min_value=-1.0, max_value=10.0, step=0.1, value=4.6, format="%f %%")
    #     taxa_apr_novos = st.slider("Taxa de Aprovação Novos", min_value=-1.0, max_value=10.0, step=0.1, value=0.6, format="%f %%")
    #     taxa_apr_recus = st.slider("Taxa de Aprovação Recusados", min_value=-1.0, max_value=10.0, step=0.1, value=0.3, format="%f %%")

    # with right:
    #     peso_custo_produto = st.number_input("Peso para Custos de Produto", value=10)
    #     peso_custo_operacao = st.number_input("Peso para Custos Operacionais", value=3)
    #     peso_outros_custos = st.number_input("Peso para Outros Custos", value=1)
    #     meses_para_pnl =  st.number_input("Meses para PnL", value=12)

    

    # return {
    #     "fee_30": fee_30,
    #     "fee_60": fee_60,
    #     "fee_90": fee_90,
    #     "peso_custo_produto": peso_custo_produto,
    #     "peso_custo_operacao": peso_custo_operacao,
    #     "peso_outros_custos": peso_outros_custos,
    #     "taxa_apr_novos": taxa_apr_novos,
    #     "taxa_apr_recus": taxa_apr_recus,
    #     "meses_para_pnl": meses_para_pnl
    # }

        return {
        "fee_30": 3,
        "fee_60": 3.8,
        "fee_90": 4.6,
        "peso_custo_produto": 10,
        "peso_custo_operacao": 3,
        "peso_outros_custos": 1,
        "taxa_apr_novos": 0.6,
        "taxa_apr_recus": 0.3,
        "meses_para_pnl": 12
    }

def calculate_results():


    if res['average_monthly_spend'] <= 500:
        faixa_ticket_medio = 0
    elif res['average_monthly_spend'] <= 1000:
        faixa_ticket_medio = 1
    elif res['average_monthly_spend'] <= 2000:
        faixa_ticket_medio = 2
    elif res['average_monthly_spend'] <= 4000:
        faixa_ticket_medio = 3
    elif res['average_monthly_spend'] <= 8000:
        faixa_ticket_medio = 4
    else:
        faixa_ticket_medio = 5



    curva_spending = [[2, 1.5, 1.4, 1.12, 1.01, 1 ], 
         [2.44, 1.65, 1.484, 1.1312, 1.01, 1],
         [2.4644, 1.65, 1.484, 1.1312, 1.01, 1],
         [2.4669, 1.65, 1.484, 1.1312, 1.01, 1],
         [2.4669, 1.65, 1.484, 1.1312, 1.01, 1],
         [2.4669, 1.65, 1.484, 1.1312, 1.01, 1],
         [2.4669, 1.65, 1.484, 1.1312, 1.01, 1],
         [2.4669, 1.65, 1.484, 1.1312, 1.01, 1],
         [2.4669, 1.65, 1.484, 1.1312, 1.01, 1],
         [2.4669, 1.65, 1.484, 1.1312, 1.01, 1],
         [2.4669, 1.65, 1.484, 1.1312, 1.01, 1],
         [2.4669, 1.65, 1.484, 1.1312, 1.01, 1]]



    ticket_medio_recusados = res['average_monthly_spend']*curva_spending[params['meses_para_pnl'] - 1][faixa_ticket_medio]
    ticket_medio_novos = 0
    for i in range(params['meses_para_pnl']):
        ticket_medio_novos = ticket_medio_novos + res['average_monthly_spend']*curva_spending[i][faixa_ticket_medio]

    ticket_medio_novos = ticket_medio_novos/params['meses_para_pnl']

    receita = []
    cmv = []
    margem_bruta = []
    sgna_costs = []
    credit_costs = []
    custos_ops = []
    margem_op = []
    outros_custos = []
    margem_liquida = []


    receita = np.append(receita, res['client_base']*res['average_monthly_spend']*params['meses_para_pnl'])
    receita = np.append(receita, res['acquitisions_per_month']*params['meses_para_pnl']*ticket_medio_novos*params['taxa_apr_novos']*(1 + params['meses_para_pnl'])/2)
    receita = np.append(receita, res['creditless_base']*ticket_medio_recusados*params['taxa_apr_recus']*params['meses_para_pnl'])
    receita = np.append(receita, receita.sum())

    perc_custo_produto = (1 - res['liquid_margins']/100)*(params['peso_custo_produto']/(params['peso_custo_produto']+params['peso_custo_operacao']+params['peso_outros_custos']))
    perc_custo_operacao = (1 - res['liquid_margins']/100)*(params['peso_custo_operacao']/(params['peso_custo_produto']+params['peso_custo_operacao']+params['peso_outros_custos']))
    perc_outros_custos = (1 - res['liquid_margins']/100)*(params['peso_outros_custos']/(params['peso_custo_produto']+params['peso_custo_operacao']+params['peso_outros_custos']))

    cmv = np.append(cmv, -receita[0]*perc_custo_produto)
    cmv = np.append(cmv, -receita[1]*perc_custo_produto)
    cmv = np.append(cmv, -receita[2]*perc_custo_produto)
    cmv = np.append(cmv, cmv.sum())

    margem_bruta = np.append(margem_bruta, receita[0]+cmv[0])
    margem_bruta = np.append(margem_bruta, receita[1]+cmv[1])
    margem_bruta = np.append(margem_bruta, receita[2]+cmv[2])
    margem_bruta = np.append(margem_bruta, receita[3]+cmv[3])

    sgna_costs = np.append(sgna_costs, -0.75*receita[0]*perc_custo_operacao)
    sgna_costs = np.append(sgna_costs, -0.75*receita[1]*perc_custo_operacao)
    sgna_costs = np.append(sgna_costs, -0.75*receita[2]*perc_custo_operacao)
    sgna_costs = np.append(sgna_costs, -0.75*receita[3]*perc_custo_operacao)

    if res['payment_term'] == 30:
        taxa_prazo = params['fee_30']/100
    elif res['payment_term'] == 60:
        taxa_prazo = params['fee_60']/100
    elif res['payment_term'] == 90:
        taxa_prazo = params['fee_90']/100

    credit_costs = np.append(credit_costs, -0.25*receita[0]*perc_custo_operacao)
    credit_costs = np.append(credit_costs, -receita[1]*taxa_prazo)
    credit_costs = np.append(credit_costs, -receita[2]*taxa_prazo)
    credit_costs = np.append(credit_costs, credit_costs.sum())

    custos_ops = np.append(custos_ops, sgna_costs[0] + credit_costs[0])
    custos_ops = np.append(custos_ops, sgna_costs[1] + credit_costs[1])
    custos_ops = np.append(custos_ops, sgna_costs[2] + credit_costs[2])
    custos_ops = np.append(custos_ops, sgna_costs[3] + credit_costs[3])

    margem_op = np.append(margem_op, margem_bruta[0] + custos_ops[0])
    margem_op = np.append(margem_op, margem_bruta[1] + custos_ops[1])
    margem_op = np.append(margem_op, margem_bruta[2] + custos_ops[2])
    margem_op = np.append(margem_op, margem_bruta[3] + custos_ops[3])

    outros_custos = np.append(outros_custos, -receita[0]*perc_outros_custos)
    outros_custos = np.append(outros_custos, -receita[1]*perc_outros_custos)
    outros_custos = np.append(outros_custos, -receita[2]*perc_outros_custos)
    outros_custos = np.append(outros_custos, outros_custos.sum())

    margem_liquida = np.append(margem_liquida, margem_op[0] + outros_custos[0])
    margem_liquida = np.append(margem_liquida, margem_op[1] + outros_custos[1])
    margem_liquida = np.append(margem_liquida, margem_op[2] + outros_custos[2])
    margem_liquida = np.append(margem_liquida, margem_liquida.sum())


    return pd.DataFrame(
        [receita, 
         cmv,
         margem_bruta,
         custos_ops,
         margem_op,
         outros_custos,
         margem_liquida]
        , columns=["BAU", "+Tino novos", "+Tino recusados", "Total"], 
        index=["(+) Receita", "(-) CMV", "(=) Margem bruta", "(-) Custo operacionais", "(=) Margem operacional", "(-) Outros custos", "(=) Margem Líquida"])



# image = Image.open('tino_logo.png')


# custom_html = """
# <div class="banner">
#     <img src="https://htmlcolorcodes.com/assets/images/colors/sunset-orange-color-solid-background-1920x1080.png" alt="Banner Image">
# </div>
# <style>
#     .banner {
#         width: 100%;
#         height: 100%;
#         overflow: visible;
#     }
#     .banner img {
#         width: 100%;
#         height: 100%;
#         object-fit: fill;
#     }
# </style>
# """
# # Display the custom HTML
# st.components.v1.html(custom_html)


button_style = {"color": "white"}
st.markdown(f"""<style> div.stButton > button:first-child {{text-align: center;background-color: #ff5c54; color: {button_style['color']}; height: auto; width: 100%;padding-top: 10px; padding-bottom: 10px;}} </style>""", unsafe_allow_html=True)



# st.button("Mark Reviewed")

# st.columns(3)[1].title("Calculadora&nbsp;Tino")

params = get_model_parameters()

with st.form("my_form"):
    res = get_main_inputs()
    # st.write(res['client_base'])

    calc = calculate_results()
    # st.write(params['fee_30'])

    submitted = st.form_submit_button("**VEJA&nbsp;SEUS&nbsp;RESULTADOS**")

    

    fig = go.Figure()

    bau_rev = calc["BAU"].iloc[0]
    new_rev = calc["Total"].iloc[0]

    bau_margin = calc["BAU"].iloc[-1] / calc["BAU"].iloc[0]
    new_margin = calc["Total"].iloc[-1] / calc["Total"].iloc[0]

    

    if submitted:
        st.write("")
        st.write("")
        st.markdown("<p style='text-align: center;font-size: 50px;color: #324138;'>Resultados</p>", unsafe_allow_html=True)


        fig.add_trace(go.Indicator(
            mode = "number+delta",
            delta = {'reference': round(bau_rev, 3), 'prefix': "R$ ", 'increasing':{'color': '#008f39'}, 'decreasing':{'color': '#fc0b0b'}},
            value = round(new_rev, 3),
            number = {'prefix': "R$ "},
            domain = {'row': 0, 'column': 0},
            title="Receita Anual"),
        )

        fig.add_trace(go.Indicator(
            mode = "number+delta",
            delta = {'reference': round(100 * bau_margin, 3), 'suffix': " p.p.", 'increasing':{'color': '#008f39'}, 'decreasing':{'color': '#fc0b0b'}},
            value = round(100 * new_margin, 3),
            number = {'suffix': " %"},
            domain = {'row': 0, 'column': 1},
            title="Margem Líquida Anual"),
        )



        fig.update_layout(
         grid = {'rows': 1, 'columns': 2, 'pattern': "coupled"}, height = 200, margin=dict(l=20, r=20, t=70, b=20),font_color="#324138",
        )


        st.plotly_chart(fig,height=300 ,use_container_width=True)

        st.write("---")

        st.markdown("<p style='text-align: center;font-size: 60px;line-height: 60px;;color: #ff5c54;'>Com o Tino, você pode mais que dobrar as vendas!</p>", unsafe_allow_html=True)

        st.markdown("<h6 style='width: 80%;margin: 0 auto; text-align: center; color: #324138;'>Você aumenta a frequência de compras e o ticket médio e o seu lojista garante mais crédito e prazo para pagar.</h6>", unsafe_allow_html=True)

        button_style = {"color": "white"}
        st.markdown(f"""<style> div.stLinkButton > a:first-child {{text-align: center;background-color: #324138; color: {button_style['color']}; height: auto; width: 100%;padding-top: 10px; padding-bottom: 10px;}} </style>""", unsafe_allow_html=True)

        st.write("")
        st.write("")

        st.link_button("FALAR COM UM CONSULTOR", "https://wa.me/5511971624475?text=Ol%C3%A1%21+Quero+adotar+o+Tino+na+minha+empresa.+", type = "primary")

        # st.table(calc)

