https://facto.conveniar.com.br/Fundacao/Forms/Convenio/ConsultaPedidoPagamento.aspx
<div class="row">
                    <!-- START .m-login -->
                    <div class="col-sm-10 col-sm-offset-1 col-md-6 col-md-offset-3 col-lg-4 col-lg-offset-4 text-center m-login">
                        
    <div id="ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_DialogUserControl1_updMensagem">
	
    
    
</div>

<div id="dialog-geral" style="display: none;">
    <div id="dialog-modal-geral" title="Mensagem">
	    <p id="divpag">
	        <span id="imagem_msg" class="mensagem info"></span>
	        <span id="span_mensagem"></span>
	    </p>
        <div id="form2"></div>
    </div>
</div>


<table id="ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario" class="login-form-panel" cellspacing="0" cellpadding="0" border="0" style="border-collapse:collapse;">
	<tbody><tr>
		<td>

        

        <div id="login-form">
            <div class="form-group form-group-lg">
                <input name="ctl00$ContentPlaceHolder1$ObjWucLoginCaptcha$lgUsuario$UserName" type="text" maxlength="50" id="ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_UserName" title="Informe seu usuário" class="form-control m-login__username login-username" placeholder="Usuário">
                <span id="ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_rfvUsuario" style="color:Red;display:none;"></span>
            </div>
            <div class="form-group form-group-lg">
                <input name="ctl00$ContentPlaceHolder1$ObjWucLoginCaptcha$lgUsuario$Password" type="password" maxlength="30" id="ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_Password" title="Informe sua senha" class="form-control m-login__password login-password" placeholder="Senha">
                <span id="ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_rfvSenha" style="color:Red;display:none;"></span>
            </div>
            
            <div class="form-control-login-btn">
                <input type="submit" name="ctl00$ContentPlaceHolder1$ObjWucLoginCaptcha$lgUsuario$btnLogin" value="Entrar" onclick="javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions(&quot;ctl00$ContentPlaceHolder1$ObjWucLoginCaptcha$lgUsuario$btnLogin&quot;, &quot;&quot;, true, &quot;lgUsuarioValidation&quot;, &quot;&quot;, false, false))" id="ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_btnLogin" class="btn btn-lg btn-block m-login__submit">
            </div>
        </div>
    </td>
	</tr>
</tbody></table>

    <em>
        <a id="ctl00_ContentPlaceHolder1_lbtnEsqueceuSenha" class="m-login__link" href="javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions(&quot;ctl00$ContentPlaceHolder1$lbtnEsqueceuSenha&quot;, &quot;&quot;, false, &quot;&quot;, &quot;Seguranca/NovaSenha.aspx&quot;, false, true))">Perdeu a senha?</a>
    </em>

                    </div>
                    <!-- END .m-login -->
                </div> coloque o login 



clique em amrcar todos <a id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_lbtTodos" href="javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions(&quot;ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$lbtTodos&quot;, &quot;&quot;, true, &quot;&quot;, &quot;&quot;, false, true))">Todos</a> depoius desmarque <input id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_chkEmpenhoContrato" type="checkbox" name="ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$chkEmpenhoContrato"> desmarque esse tambem <input id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_chkFolhaPagamento" type="checkbox" name="ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$chkFolhaPagamento">


depois apague <li>
                        <label>Data do Pedido:</label>
                            <input name="ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$txtDataInicial" type="text" maxlength="10" id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_txtDataInicial" class="datepicker defaultdate hasDatepicker" data-m-prev="3" onkeydown="return MascaraData(event,this)" style="width:80px;" autocomplete="off">
                            <span id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_CvdDataInicial" style="color:Red;display:none;">Campo inválido</span>-
                            <input name="ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$txtDataFinal" type="text" maxlength="10" id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_txtDataFinal" class="datepicker hasDatepicker" onkeydown="return MascaraData(event,this)" style="width:80px;" autocomplete="off">
                            <span id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_cvdDataFinal" style="color:Red;visibility:hidden;">Campo inválido</span>
                        </li> e apague <li>
                            <label>Data de Vencimento:</label>
                            <input name="ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$txtDataVencimentoInicial" type="text" maxlength="10" id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_txtDataVencimentoInicial" class="datepicker defaultdate hasDatepicker" data-m-prev="3" onkeydown="return MascaraData(event,this)" style="width:80px;" autocomplete="off">
                            <span id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_CvdDataVencimentoInicial" style="color:Red;display:none;">Campo inválido</span>-
                            <input name="ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$txtDataVencimentoFinal" type="text" maxlength="10" id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_txtDataVencimentoFinal" class="datepicker hasDatepicker" onkeydown="return MascaraData(event,this)" style="width:80px;" autocomplete="off">
                            <span id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_cvdDataVencimentoFinal" style="color:Red;visibility:hidden;">Campo inválido</span>
                        </li> aqui quero que insira o numero do pedido <input name="ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$txtNumPedido" type="text" maxlength="20" id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_txtNumPedido" class="numeroPedido" style="width:80px;"> clique em consultar <input type="submit" name="ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$btnConsultar" value="Consultar" onclick="javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions(&quot;ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$btnConsultar&quot;, &quot;&quot;, true, &quot;&quot;, &quot;&quot;, false, false))" id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_btnConsultar"> e aguarde o loader sumir da tela (essa funcao vai ser usada apos qualquer iteracao no site e use uma funcao pra ela usando invisibiliy element wait ) <div id="imgLoad">
                                    <img id="ctl00_Image2" src="../../Imagens/aniAjaxLoad2.gif" style="border-width:0px;">
                                </div> 


                                quero que aguarde a imagem sumir depois quero que pegue e confirme se o resultado é o esperado 
 confirme e depois quero que clique no botao editar da linha <tr class="gridRow" style="cursor:pointer">
			<td align="center">
                                <span class="ckItemDoc"><input id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_gvPrincipal_ctl02_ckItemDoc" type="checkbox" name="ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$gvPrincipal$ctl02$ckItemDoc"></span>
                                <input type="hidden" name="ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$gvPrincipal$ctl02$CodPedido" id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_gvPrincipal_ctl02_CodPedido" value="305122">
                                <input type="hidden" name="ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$gvPrincipal$ctl02$CodTipoPedido" id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_gvPrincipal_ctl02_CodTipoPedido" value="65">
                                <input type="hidden" name="ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$gvPrincipal$ctl02$CodStatus" id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_gvPrincipal_ctl02_CodStatus" value="17">
                            </td><td class="ignore-click">
                                <div id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_gvPrincipal_ctl02_UpdExcluir">
				
                                        <a id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_gvPrincipal_ctl02_lbtCancelar" title="Cancelar registro" href="javascript:__doPostBack('ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$gvPrincipal$ctl02$lbtCancelar','')">
                                            <span class="tema excluir"></span>
                                        </a>
                                    
			</div>
                            </td><td class="ignore-click">
                                <div id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_gvPrincipal_ctl02_updEditar">
				
                                        <a id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_gvPrincipal_ctl02_lbtEditar" title="Editar registro" href="javascript:__doPostBack('ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$gvPrincipal$ctl02$lbtEditar','')">
                                            <span class="tema editar"></span>
                                        </a>
                                    
			</div>
                            </td><td align="right" style="width:1.8cm;">56555/2026</td><td style="width:5cm;">Retribuição Pecuniária</td><td align="right" style="width:1.3cm;">374</td><td style="width:6cm;">PS TÉCNICO 2027/1 e 2027/2</td><td style="width:5cm;">SANANDREIA TOREZANI PERINNI</td><td style="width:5cm;">DANIELLE CRISTINE MORAES DE AZEVEDO</td><td align="right" style="width:2.5cm;">06/11/2026</td><td align="right" style="width:2.5cm;">06/11/2026</td><td align="right" style="width:2.5cm;">09/11/2026</td><td align="right" style="width:2cm;">558,02</td><td style="width:3cm;">Aprovado</td><td class="ignore-click" align="center">
                                <div id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_gvPrincipal_ctl02_UpdHistorico">
				
                                        <a id="ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_gvPrincipal_ctl02_lbtHistorico" title="Histórico" href="javascript:__doPostBack('ctl00$ContentPlaceHolder1$ConsultaPedidoPagamentoUserControl2$gvPrincipal$ctl02$lbtHistorico','')">
                                            <span class="tema selecionarTabela"></span>
                                        </a>
                                    
			</div>
                            </td>
		</tr> para abrir o pedido, depois disso aguarde que direi o restante
