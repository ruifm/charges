#include <stdio.h>
#include <gtk/gtk.h>
#include <cairo.h>
#include <time.h>
#include <stdlib.h>
#include <math.h>
#include "vector.h"
#include "eletric.h"

#define PONTOS 400
// variaveis globais
// sao variaveis necessarias num grande numero de funcoes como alguns widgets principais
// e sobretudo, controladores e switches
charge q[TOTAL], q_p[TOTAL];
static double dt = 1e-5;
int mov=1;
int action=0, contador=0;
int c=1,j=-1,n=0,bound=1,trail=1,openg=0,scale_c=0;
vector l[PONTOS];
char a_res[30],v_res[30];
int limit;
int do_get=0;
double a[PONTOS],s[PONTOS],regis[PONTOS],k1=1,k2=1,kt=10;
GtkWidget *timer,*erro,*res;
char buffer[256];
clock_t t0, p;
double temp=0,mostra;
GtkWidget *controlo_carga[TOTAL], *controlo_massa[TOTAL];
GtkWidget *controlo_vinicial[2], *legenda_vinicial[2];
GtkWidget *combo, *entry[4];
GtkWidget *screen,*graph,*alterar;
GtkWidget *fronteira,*rasto, *pausa,*reset;
GtkWidget *v_label,*a_label;
GtkWidget *s_s,*s_a,*s_t;
int conta_j=1;


                                   /*****FUNCOES CALLBACK******/


// CALLBACKS dos sliders
void mudar_carga (GtkWidget *slider, int i)
{
  q[i].qt = (double) gtk_range_get_value(GTK_RANGE(slider));
}

void mudar_massa (GtkWidget *slider, int i)
{
  q[i].mass = (double) gtk_range_get_value(GTK_RANGE(slider));
  q[i].radius = (double) gtk_range_get_value(GTK_RANGE(slider));
}

void mudar_vel_x (GtkWidget *slider) 
{
  q[0].vel.x = (double) gtk_range_get_value(GTK_RANGE(slider));
}


void mudar_vel_y (GtkWidget *slider)
{
	q[0].vel.y = (double) gtk_range_get_value(GTK_RANGE(slider));  
}
void valor_escala(GtkWidget *slider,int e){
	switch(e){
		case 1:
			k1=gtk_range_get_value(GTK_RANGE(slider));
			break;
		case 2:
			k2=gtk_range_get_value(GTK_RANGE(slider));
			break;
		case 3:
			kt=gtk_range_get_value(GTK_RANGE(slider));
			break;
	}
}

//Callback do about
void show_about(GtkWidget *widget, gpointer data)
{

  GdkPixbuf *pixbuf = gdk_pixbuf_new_from_file("images/ist.png", NULL);

  GtkWidget *dialog = gtk_about_dialog_new();
  gtk_about_dialog_set_name(GTK_ABOUT_DIALOG(dialog), "Simulador de Cargas");

  gtk_about_dialog_set_version(GTK_ABOUT_DIALOG(dialog), "1.0"); 

  gtk_about_dialog_set_copyright(GTK_ABOUT_DIALOG(dialog), 
      "Trabalho realizado no ambito da cadeira de Programacao. \n"
      "Para mais informacoes, abra o menu Instrucoes.");

  gtk_about_dialog_set_comments(GTK_ABOUT_DIALOG(dialog), 
     "André Melo e Rui Marques\nIST | MEFT | 2012");

  gtk_about_dialog_set_logo(GTK_ABOUT_DIALOG(dialog), pixbuf);

  g_object_unref(pixbuf), pixbuf = NULL;
  gtk_dialog_run(GTK_DIALOG (dialog));
  gtk_widget_destroy(dialog);

}
// callback de abrir a janela de escalas
void change_scale(GtkWidget *widget, int data){
	scale_c= data;
	if(scale_c)
		gtk_widget_show_all(alterar);
	else
		gtk_widget_hide_on_delete(alterar);
}

//Callback de abrir grafico
void abrir_grafico(GtkWidget *widget, int data){
	openg= data;
	if(openg)
		gtk_widget_show(graph);
	else
		gtk_widget_hide_on_delete(graph);
}


//Callback de fechar grafico
gboolean quick_message (GtkWidget *win) 
{

  GtkWidget *dialog, *label;
  gchar *message = "Tem a certeza que quer sair?";
  gint  resultado ;
     
  dialog = gtk_dialog_new_with_buttons ("Message",
                                         GTK_WINDOW(win),
                                         GTK_DIALOG_DESTROY_WITH_PARENT,
                                         GTK_STOCK_YES,
                                         GTK_RESPONSE_YES,
                                         GTK_STOCK_NO,
                                         GTK_RESPONSE_NO,
                                         NULL);
   gtk_window_set_default_size (GTK_WINDOW(dialog), 250, 120);
   
   gtk_window_set_modal (GTK_WINDOW (dialog), TRUE);
   label = gtk_label_new (message);
   
   gtk_container_add (GTK_CONTAINER (GTK_DIALOG(dialog)->vbox), label);
   gtk_widget_show_all (dialog);

   resultado = gtk_dialog_run (GTK_DIALOG(dialog));
   gtk_widget_destroy(dialog);

   if (resultado == GTK_RESPONSE_YES)
     return TRUE;
   else
     return FALSE;
}

//FECHAR JANELA

gboolean Teste_BotaoSair (GtkWidget *w, GtkWidget *win) 
{
  gboolean teste ;

  teste = quick_message (win);
  if (!teste)
    return TRUE;

  gtk_main_quit();
  return FALSE;
}

gboolean Teste_DeleteEvent (GtkWidget *w, GtkWidget *w1, GtkWidget *win) 
{
  gboolean teste ;

  teste = quick_message (win);
  if (!teste)
    return TRUE;

  gtk_main_quit();
  return FALSE;
}
	
//ABRIR INSTRUÇÕES
int show_instructions(GtkWidget *widget, gpointer window)
{
	return system ("evince relatorio.pdf &");
}	


// CALLBACK do botao de pausa
static void tempo(GtkWidget *widget)
{
	contador++;
	action= contador % 2;
	if(action){
 		gtk_button_set_label(GTK_BUTTON(widget),"Pausa");
 		if(contador>1)
 			temp += (double)(clock()-p)/(double)CLOCKS_PER_SEC; /* tempo que esta em pausa */
 	}
 	else{
 		gtk_button_set_label(GTK_BUTTON(widget),"Continuar");
 		p=clock();
 	}	
 	if(contador==1)
 		t0=clock();
}


// CALLBACK do reset
static void limpa(GtkWidget *widget){
	int i;
	if(action)
		tempo(pausa);
	
	gtk_button_set_label(GTK_BUTTON(pausa),"Iniciar");	
	c=1;
	t0=clock();
	temp=0;
	contador=action;
	j=-1;
	n=0;
	limit=1;
	k1=1.;
	k2=1.;
	q[0].a.x=q[0].a.y=0;
	gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(fronteira),TRUE);
	gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(rasto),TRUE);
	
	gtk_label_set_text(GTK_LABEL(timer),"Tempo: 0.0 s");
	gtk_label_set_text(GTK_LABEL(erro),"Nenhum erro");
	gtk_label_set_text(GTK_LABEL(res)," ");
	gtk_label_set_text(GTK_LABEL(v_label),"Velocidade: 0");
	gtk_label_set_text(GTK_LABEL(a_label),"Aceleracao: 0");
	
	gtk_range_set_value(GTK_RANGE(controlo_vinicial[0]),0);
	gtk_range_set_value(GTK_RANGE(controlo_vinicial[1]),0);
	
	gtk_range_set_value(GTK_RANGE(s_s),1.);
	gtk_range_set_value(GTK_RANGE(s_a),1.);
	gtk_range_set_value(GTK_RANGE(s_t),10.);
	
	gtk_combo_box_set_active(GTK_COMBO_BOX(combo),-1);
	
	for(i=0;i<TOTAL;i++)
	{
		gtk_entry_set_text(GTK_ENTRY(entry[i]),"");
		gtk_range_set_value(GTK_RANGE(controlo_carga[i]),0);
		gtk_range_set_value(GTK_RANGE(controlo_massa[i]),15);
	}

}

// CALLBACK do random
static void apply_random(GtkWidget *widget)
{
	double x_total,y_total;
	int i;
	gint width, height;
  
  gtk_window_get_size(GTK_WINDOW(screen), &width, &height);
  
  x_total=0.6*width;
  y_total=20./22. * height;
	
	if(action)
		tempo(pausa);
	limpa(reset);
	
	c=0;
	
	srand(time(NULL));
	        
	for(i=0; i<TOTAL; i++){
	  q[i].qt = (((double) rand() / (double) RAND_MAX)*100 - 50);
	  gtk_range_set_value(GTK_RANGE(controlo_carga[i]), q[i].qt);
	 
	 	q[i].mass = (((double) rand() / (double) RAND_MAX)*10 + 5);
	 	q[i].radius=q[i].mass;
	  gtk_range_set_value(GTK_RANGE(controlo_massa[i]), q[i].mass);
	
		q[i].pos.x=((double) rand() / (double) RAND_MAX)*(x_total-q[i].radius)*0.7+q[i].radius;
		q[i].pos.y=((double) rand() / (double) RAND_MAX)*(y_total-q[i].radius)*0.7+q[i].radius;
	}
	
	q[0].vel.x = (((double) rand() / (double) RAND_MAX)*1000 - 500);
	gtk_range_set_value(GTK_RANGE(controlo_vinicial[0]), q[0].vel.x);
	q[0].vel.y = (((double) rand() / (double) RAND_MAX)*1000 - 500);
	gtk_range_set_value(GTK_RANGE(controlo_vinicial[1]), q[0].vel.y);
	
	tempo(pausa);
}

//CALLBACK da DEMO
static void apply_demo(GtkWidget *widget)
{
	gint width, height;
  gtk_window_get_size(GTK_WINDOW(screen), &width, &height);
  double x_total,y_total;
  x_total=0.6*width;
  y_total=20./22. * height;

	if(action)
		tempo(pausa);

	limpa(reset);
	c=0;
	int i;

	q[0].qt=-10.;
	q[1].qt=10.;
	q[2].qt=12.;
	q[3].qt=10.;
	
	q[0].radius=10;
	q[1].radius=10;
	q[2].radius=10;
	q[3].radius=10;
	
	q[0].mass=10;
	q[1].mass=10;
	q[2].mass=10;
	q[3].mass=10;
	
	q[0].vel.x=50;
	q[0].vel.y=-100;
	
	q[0].pos.x=x_total/2.;
	q[0].pos.y=y_total/2.;
	
	q[1].pos.x=q[0].pos.x+100;
	q[1].pos.y=q[0].pos.y+100;
	
	q[2].pos.x=q[0].pos.x-100;
	q[2].pos.y=q[0].pos.y+100;
	
	q[3].pos.x=q[0].pos.x;
	q[3].pos.y=q[0].pos.y-100;
	
	gtk_range_set_value(GTK_RANGE(controlo_vinicial[0]),q[0].vel.x);
	gtk_range_set_value(GTK_RANGE(controlo_vinicial[1]),q[0].vel.y);
	
	for(i=0;i<TOTAL;i++)
	{
		gtk_range_set_value(GTK_RANGE(controlo_carga[i]),q[i].qt);
	
		gtk_range_set_value(GTK_RANGE(controlo_massa[i]),q[i].mass);
	}
	
	tempo(pausa);
	
}
 

// CALLBACK do mouseclick
static gboolean clicked(GtkWidget *widget, GdkEventButton *event,gpointer data)
{
	gint width, height;
  gtk_window_get_size(GTK_WINDOW(widget), &width, &height);
    
    if (event->button == 1) {
    
    	if((event->x > 0)               							&& 
    	   ((event->x)+q[mov].radius<width*(6./10.))  && 
    	   (event->y > q[mov].radius) 								&& 
    	   ((event->y)+q[mov].radius < (20./22.)*height))
    	   {
        	q[mov].pos.x=event->x;
        	q[mov].pos.y=event->y;
        }        
    }

    if (event->button == 3) 
    		gtk_widget_queue_draw(widget);
    

    return TRUE;
}


// CALLBACK dos radiobuttons
static void radio_change(GtkWidget *widget, int i)
{
	mov=i;
}


// CALLBACK do botao calcular
static void calcular(GtkWidget *widget)
{
	char b2[250];
	gint width, height;
  gtk_window_get_size(GTK_WINDOW(screen), &width, &height);
	double value[4];
	int i,teste[TOTAL];
	
	gtk_label_set_text(GTK_LABEL(erro),"Nenhum erro");
	gtk_label_set_text(GTK_LABEL(res)," ");

	for(i=0;i<TOTAL;i++)
		teste[i]=sscanf(gtk_entry_get_text(GTK_ENTRY(entry[i])),"%lf",&value[i]);
		
	for(i=0;i<TOTAL;i++)
		{
			switch(gtk_combo_box_get_active(GTK_COMBO_BOX(combo))){
				case -1:
					gtk_label_set_text(GTK_LABEL(erro),"Nao selecionou nenhuma opcao");
					break;	
				
				case 0:
					{
				
						if(teste[i])
						{
							if(fabs(value[i])<=50)
								{
									q[i].qt=value[i];
									gtk_range_set_value(GTK_RANGE(controlo_carga[i]),value[i]);
									gtk_label_set_text(GTK_LABEL(res),"Calculo da carga efectuado");
								}
					
							else
								{
									sprintf(b2,"Carga de %s muito elevado",q[i].name);
									gtk_label_set_text(GTK_LABEL(erro),b2);
								}
						}
				
					else
						{
							sprintf(b2,"Entrada de %s invalida",q[i].name);
							gtk_label_set_text(GTK_LABEL(erro),b2);
						}
				}
				break;
			
			
			case 1:
				{
			
				if((teste[i]) && (value[i]))
					{
						if( ((value[i]<=25) && (value[i]>=5)) || (value[i]==0))
							{
								if(value[i])
									{
										q[i].mass=value[i];
										q[i].radius=value[i];
										gtk_range_set_value(GTK_RANGE(controlo_massa[i]),value[i]);
									}
								gtk_label_set_text(GTK_LABEL(res),"Calculo da massa/raio efectuado");
							}			
					
						else
							{
								sprintf(b2,"Massa de %s muito elevado/baixo",q[i].name);
								gtk_label_set_text(GTK_LABEL(erro),b2);
							}
					}
				
				else
					{
						sprintf(b2,"Entrada de %s invalida",q[i].name);
						gtk_label_set_text(GTK_LABEL(erro),b2);
					}
					
				}	
				
				break;
				
			case 2:
				{
				
					if(teste[i])
						{
							if(fabs(value[i])<=500)
								{
									q[i].vel.x=value[i];
									gtk_range_set_value(GTK_RANGE(controlo_vinicial[0]),value[i]);
									gtk_label_set_text(GTK_LABEL(res),"Calculo de vel x efectuado");
								}

							else
								{
									sprintf(b2,"Velocidade de %s muito elevado",q[i].name);
									gtk_label_set_text(GTK_LABEL(erro),b2);
								}
						}
						
					else
						{
							sprintf(b2,"Entrada de %s invalida",q[i].name);
							gtk_label_set_text(GTK_LABEL(erro),b2);
						}
				}
				
				break;
			
			case 3:
				{
					if(teste[i])
						{
							if(fabs(value[i])<=500)
								{
									q[i].vel.y=value[i];
									gtk_range_set_value(GTK_RANGE(controlo_vinicial[1]),value[i]);
									gtk_label_set_text(GTK_LABEL(res),"Calculo de vel y efectuado");
								}
					
							else
								{
									sprintf(b2,"Velocidade de %s muito elevado",q[i].name);
									gtk_label_set_text(GTK_LABEL(erro),b2);
								}
						}
				
				else
					{
						sprintf(b2,"Entrada de %s invalida",q[i].name);
						gtk_label_set_text(GTK_LABEL(erro),b2);
					}
				}
				
				break;
				
			case 4:
				{
					if(teste[i])
						{
							if((value[i] > q[0].radius)&&((value[i]+q[i].radius)<width*(6./10.)))
								{
									q[i].pos.x=value[i];
									gtk_label_set_text(GTK_LABEL(res),"Calculo de pos x efectuado");
								}
							
							else
								{
									sprintf(b2,"Posicao de %s fora da janela",q[i].name);
									gtk_label_set_text(GTK_LABEL(erro),b2);
								}
						}
				
					else
						{
							sprintf(b2,"Entrada de %s invalida",q[i].name);
							gtk_label_set_text(GTK_LABEL(erro),b2);
						}
				}
				
//se você está a ler isto, claramente está perdido
				break;
				
				
			case 5:
				{
					if(teste[i])
						{
							if((value[i] > q[i].radius)&&((value[i]+q[i].radius) < (20./22.)*height))
								{
									q[i].pos.y=value[i];
									gtk_label_set_text(GTK_LABEL(res),"Calculo de pos y efectuado");
								}
				
							else
								{
									sprintf(b2,"Posicao de %s fora da janela",q[i].name);
									gtk_label_set_text(GTK_LABEL(erro),b2);
								}
						}
						
						
				else
						{
							sprintf(b2,"Entrada de %s invalida",q[i].name);
							gtk_label_set_text(GTK_LABEL(erro),b2);
						}
				}
		}
	}
}


// CALLBACK de mudar combo
static void cleared(GtkWidget *widget)
{
	gtk_entry_set_text(GTK_ENTRY(entry[0]),"");
	gtk_entry_set_text(GTK_ENTRY(entry[1]),"");
	gtk_entry_set_text(GTK_ENTRY(entry[2]),"");
	gtk_entry_set_text(GTK_ENTRY(entry[3]),"");
	gtk_label_set_text(GTK_LABEL(erro),"Nenhum erro");
	gtk_label_set_text(GTK_LABEL(res)," ");
}


// CALLBACK do fronteiras checkbutton
static void border(GtkWidget *widget)
{
	if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(widget)))
		bound=1;
	else
		bound=0;
}


//CALLBACK do rasto checkbutton
static void set_trail(GtkWidget *widget)
{
	if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(widget)))
		trail=1;
	else
		trail=0;
}

//CALLBACK de guardar ponto
static void save_point(GtkWidget *widget)
{
	q_p[0] = q[0];
	q_p[1] = q[1];
	q_p[2] = q[2];
	q_p[3] = q[3];

	do_get = 1;
}


//CALLBACK recuperar ponto
static void get_point(GtkWidget *widget)
{
	int i;
	
	if(do_get)
	{
		j=-1;
		n=0;
		limit=1;
		q[0] = q_p[0];
		q[1] = q_p[1];
		q[2] = q_p[2];
		q[3] = q_p[3];

		gtk_range_set_value(GTK_RANGE(controlo_vinicial[0]),q_p[0].vel.x);
		gtk_range_set_value(GTK_RANGE(controlo_vinicial[1]),q_p[0].vel.y);
	
		for(i=0;i<TOTAL;i++)
		{
			gtk_range_set_value(GTK_RANGE(controlo_carga[i]),q_p[i].qt);
			gtk_range_set_value(GTK_RANGE(controlo_massa[i]),q_p[i].mass);
		}
	}	
	
	else
	{
		GtkWidget *dialog, *label;
  	gchar *message = "ERRO: Nenhum estado guardado.";
		dialog = gtk_dialog_new_with_buttons ("Message",
  	                                     GTK_WINDOW(screen),
                                         GTK_DIALOG_DESTROY_WITH_PARENT,
                                         GTK_STOCK_OK,
                                         GTK_RESPONSE_OK,
                                         NULL);
   	gtk_window_set_default_size (GTK_WINDOW(dialog), 250, 120);
   
   	gtk_window_set_modal (GTK_WINDOW (dialog), TRUE);
   	label = gtk_label_new (message);
   
   	gtk_container_add (GTK_CONTAINER (GTK_DIALOG(dialog)->vbox), label);
   	gtk_widget_show_all (dialog);
	 	gtk_dialog_run(GTK_DIALOG (dialog));
   	gtk_widget_destroy(dialog);
  }
	
}

                              /*****Animacao******/

gboolean on_expose_event (GtkWidget *widget,GdkEventExpose *event,gpointer data){
	int i;
  cairo_t *cr ;
  gint width, height,height2;
	
	height2=600;
	
	
  gtk_window_get_size(GTK_WINDOW(widget), &width, &height);
  
  cr = gdk_cairo_create(widget->window);
  cairo_set_line_width (cr, 0.5);
  
  // Cargas fixas
  	// condicoes iniciais
  if(c)
  {
  	q[3].pos.x=(1./10.)*width;
  	q[3].pos.y=(4./22.)*height;
  	q[3].radius=15.;
  	q[3].mass=15.;
  	q[1].pos.x=(4./10.)*width;
  	q[1].pos.y=(12.3/22.)*height;
  	q[2].radius=15.;
  	q[2].mass=15.;
  	q[2].pos.x=(3./10.)*width;
  	q[2].pos.y=(16./22.)*height;
  	q[2].radius=15.;
  	q[2].mass=15.;
  }
  
  cairo_arc (cr, q[3].pos.x,q[3].pos.y, q[3].radius, 0, 2. * M_PI);
  cairo_stroke_preserve (cr);
  
  cairo_set_source_rgb (cr, 0, 0, 1);
  cairo_fill (cr);
  
  cairo_arc (cr, q[1].pos.x,q[1].pos.y, q[1].radius, 0, 2. * M_PI);
  cairo_stroke_preserve (cr);
  
  cairo_set_source_rgb (cr, 0, 1, 0);
  cairo_fill (cr);
  
  cairo_arc (cr, q[2].pos.x,q[2].pos.y,q[2].radius, 0, 2. * M_PI);
  cairo_stroke_preserve (cr);
  
  cairo_set_source_rgb (cr, 1, 0, 0);
  cairo_fill (cr);
  
  // Carga livre
  
  cairo_set_source_rgb(cr, 0, 0, 0);
	
	
  double x0=(3./10.)*width;
  double y0=(10./22.)*height;
  
  // Condicoes iniciais
  
  if(c)
  {
  	q[0].vel.x=0;
  	q[0].vel.y=0;
  	q[0].pos.x=x0;
  	q[0].pos.y=y0;
  	q[0].radius=15.;
  	q[0].mass=15.;
  }
  
  cairo_arc (cr, q[0].pos.x, q[0].pos.y, q[0].radius, 0, 2. * M_PI);
  cairo_stroke_preserve (cr);
  cairo_set_source_rgb (cr, 0, 0, 0);
  cairo_fill (cr);
  
  if(action)
  {
  	mostra=((double)(clock()-t0)/(double)CLOCKS_PER_SEC);
  	sprintf(buffer,"Tempo: %.1lf s",mostra-temp);
  	gtk_label_set_text(GTK_LABEL(timer),buffer);
  
  	// Bordas
  	for(i=0;i<1000;i++)
  		{
					if(bound)
						{
							if ((q[0].pos.x < q[0].radius) 
							|| ((q[0].pos.x+q[0].radius ) > width*(6./10.)))
									q[0].vel.x = - q[0].vel.x;
				
				
							if ((q[0].pos.y < q[0].radius) 
							|| ((q[0].pos.y+q[0].radius) > (20./22.)*height))
									q[0].vel.y = -q[0].vel.y;
						
						}
						
						
			// Mov (Euler-Cromer) - ver eletric.c e vector.c para intepretar funcoes
			
			q[0].force=factor(q[0].qt,eletric(q));
			q[0].a=factor((double)1./q[0].mass,q[0].force);
			q[0].vel = add(q[0].vel,factor(dt,q[0].a));
			q[0].pos = add(q[0].pos,factor(dt,q[0].vel));
		}
	}

		// Rasto
		
		j++;
		if(j==PONTOS)
		{
			j=0;
			n=1;
		}
		
		if(n)
			limit=PONTOS;
		else
			limit=j;
			
		l[j]=q[0].pos;
		
		double t=kt*(mostra-temp);
		regis[j]=t;
		s[j]=sqrt(norma(q[0].vel));
		a[j]=sqrt(norma(q[0].a));
		
		if(s[j]>((double)height2/2-10)/k1)
			k1=((double)height2/2-10)/s[j];
		
		if(a[j]>((double)height2/2-10)/k2)
			k2=((double)height2/2-10)/a[j];
		
		gtk_range_set_value(GTK_RANGE(s_s),k1);
		gtk_range_set_value(GTK_RANGE(s_a),k2);
		
		sprintf(a_res,"Aceleracao: %.1lf",sqrt(norma(q[0].a)));
		sprintf(v_res,"Velocidade: %.1lf",sqrt(norma(q[0].vel)));
		
		gtk_label_set_text(GTK_LABEL(v_label),v_res);
		gtk_label_set_text(GTK_LABEL(a_label),a_res);
		
		if(trail)
			{
				cairo_set_line_width(cr,2);
				
				for(i=1;i<limit;i++)
					{
						if(regis[i]>regis[i-1])
							{
								cairo_move_to(cr, l[i-1].x, l[i-1].y);
								cairo_line_to(cr, l[i].x, l[i].y);
							}
					}
			}
			
	cairo_stroke(cr);
  cairo_destroy(cr);
  
	c=0;

  
  return FALSE;
}

//Funcao que certifica a periodicidade (timeout)

static gboolean time_handler (GtkWidget *widget)
{
  if (widget->window == NULL) 
    return FALSE;
	
	gtk_widget_queue_draw(widget);

	if(graph->window != NULL)
		gtk_widget_queue_draw(graph);

  return TRUE;
}
  

// PLOTTING
void plot (GtkWidget *widget,GdkEventExpose *event,gpointer data)
{
	cairo_t *cr ;
	int i;
	char buf[50];
  gint width, height;
  gtk_window_get_size(GTK_WINDOW(widget), &width, &height);
  cr = gdk_cairo_create(widget->window);
		
	for(i=1;i<limit;i++)
		{
			if(regis[i]>regis[i-1]
			&&(fmod(regis[i],width-40)>fmod(regis[i-1],width-40)))
				{
					cairo_move_to(cr,40+fmod(regis[i-1],width-40),-10+-height/2+height-k1*s[i-1]);
					cairo_line_to(cr,40+fmod(regis[i],width-40),-10-height/2+height-k1*s[i]);
				}
		}
		
	cairo_set_source_rgb (cr, 0, 0, 1);
	cairo_stroke(cr);
	cairo_fill(cr);
	
	for(i=1;i<limit;i++)
		{
			if((regis[i]>regis[i-1])
			&&(a[i]>10)&&(a[i-1]>10)
			&&(fmod(regis[i],width-40)>fmod(regis[i-1],width-40))
			&&(k2*a[i]<height/2-10)
			&&(k2*a[i-1]<height/2-10))
				{
					cairo_move_to(cr,40+fmod(regis[i-1],width-40),height-k2*a[i-1]);
					cairo_line_to(cr,40+fmod(regis[i],width-40),height-k2*a[i]);
				}
		}
	
	cairo_set_source_rgb (cr, 1, 0, 0);
	cairo_stroke(cr);
	
	cairo_move_to(cr,40,0);			/* eixo y da vel */
	cairo_line_to(cr,40,height/2-10);
	
	cairo_move_to(cr,40,height/2-10); /* eixo x da vel */
	cairo_line_to(cr,width,height/2-10);
	
	cairo_move_to(cr,40,height/2+10); /* eixo do x da aceleracao */
	cairo_line_to(cr,width,height/2+10);
	
	cairo_move_to(cr,40,height/2+10); /* eixo do y da aceleracao */
	cairo_line_to(cr,40,height);
	cairo_set_source_rgb(cr,0,0,0);
	// graudacao
	cairo_move_to(cr, 35, 72);
	cairo_line_to(cr, 45, 72);
	cairo_move_to(cr, 5, 72);
	sprintf(buf,"%.1lf",3*((height/2)-10)/(4*k1));
	cairo_show_text(cr,buf);
	
	cairo_move_to(cr,35, 150);
	cairo_line_to(cr,45, 150);
	cairo_move_to(cr,5, 150);
	sprintf(buf,"%.1lf",2*((height/2)-10)/(4*k1));
	cairo_show_text(cr,buf);
	
	cairo_move_to(cr,35, 222);
	cairo_line_to(cr,45, 222);
	cairo_move_to(cr,5, 222);
	sprintf(buf,"%.1lf",((height/2)-10)/(4*k1));
	cairo_show_text(cr,buf);
	
	cairo_move_to(cr, 35, 372);
	cairo_line_to(cr, 45, 372);
	cairo_move_to(cr, 5, 372);
	sprintf(buf,"%.1lf",3*((height/2)-10)/(4*k2));
	cairo_show_text(cr,buf);
	
	cairo_move_to(cr,35, 450);
	cairo_line_to(cr,45, 450);
	cairo_move_to(cr,5, 450);
	sprintf(buf,"%.1lf",2*((height/2)-10)/(4*k2));
	cairo_show_text(cr,buf);
	
	cairo_move_to(cr,35, 522);
	cairo_line_to(cr,45, 522);
	cairo_move_to(cr,5, 522);
	sprintf(buf,"%.1lf",((height/2)-10)/(4*k2));
	cairo_show_text(cr,buf);
	cairo_stroke(cr);
	cairo_set_source_rgb(cr,0,0,0);
	//label de velociade
	cairo_move_to(cr, width/2-20, 15);
	sprintf(buf,"V(t) = %.1lf",s[j]);
	cairo_show_text(cr, buf);
	
	cairo_move_to(cr,width/2-20,25);
	sprintf(buf,"Escala: %.4lf",k1);
	cairo_show_text(cr,buf);
	// label de aceleracao
	cairo_move_to(cr, width/2-20, 330);
	sprintf(buf,"A(t) = %.1lf",a[j]);
	cairo_show_text(cr, buf);
	
	cairo_move_to(cr,width/2-20,340);
	sprintf(buf,"Escala: %.6lf",k2);
	cairo_show_text(cr,buf);
	// label do tempo
	cairo_move_to(cr,width/2-50,height/2);
	sprintf(buf,"Tempo: %.1lf",mostra-temp);
	cairo_show_text(cr,buf);
	
	cairo_move_to(cr,width/2+20,height/2);
	sprintf(buf,"Escala: %.1lf",kt);
	cairo_show_text(cr,buf);
	
	cairo_stroke(cr);
	cairo_fill(cr);
	
  cairo_destroy(cr);
}





int main (int argc, char *argv[])
{
	q[1].radius=15;
	q[1].mass=15;
  int i,j,k;

	sprintf(q[0].name,"q%i",0);
	sprintf(q[1].name,"Q%i",1);
	sprintf(q[2].name,"Q%i",2);
	sprintf(q[3].name,"Q%i",3);
  
  // Widgets a criar
  GtkWidget *tabela, *campo; 
  GtkWidget *legenda_carga[TOTAL];
  GtkWidget *legenda_massa[TOTAL];
  GtkObject *def_vinicial[2], *def_carga[TOTAL], *def_massa[TOTAL];;
  GtkWidget *compute, *demo, *random;
  GtkWidget *frame_massa, *frame_vinicial, *frame_carga;
  GtkWidget *preto, *vermelho, *verde, *azul, *radio[TOTAL];
  GtkWidget *opcoes, *about, *fechar, *instrucoes,*abrir, *new_point, *recover_point, *filemenu, *menubar, *vbox,*escala_g;
  GtkWidget *texto;
  GtkWidget *caixa;
  GtkObject *a_s,*a_a,*a_t;
  GtkWidget *l_s,*l_a,*l_t;
  
  gtk_init (&argc, &argv);
  
  // icon das janelas
  gtk_window_set_default_icon_from_file("images/icon.png",NULL);
  
  //parametros da janela de graficos
  graph = gtk_window_new (GTK_WINDOW_TOPLEVEL);
  gtk_window_set_title (GTK_WINDOW (graph), "Graficos");
  gtk_widget_set_size_request(graph,400,600);
  gtk_widget_set_app_paintable (graph, TRUE);
  gtk_window_set_position(GTK_WINDOW(graph), GTK_WIN_POS_CENTER);
  gtk_window_set_resizable(GTK_WINDOW(graph), FALSE);

  
  //parametros da janela principal
  screen = gtk_window_new (GTK_WINDOW_TOPLEVEL);
  gtk_window_set_title (GTK_WINDOW (screen), "Painel de Cargas");
  gtk_widget_set_size_request(screen,1200,700);
  gtk_widget_set_app_paintable (screen, TRUE);
  gtk_window_set_resizable(GTK_WINDOW(screen), FALSE);
  
  //parametros da janela da escala dos graficos
  alterar = gtk_window_new (GTK_WINDOW_TOPLEVEL);
  gtk_window_set_title (GTK_WINDOW (alterar), "Escalas");
  gtk_widget_set_size_request(alterar,500,500);
  gtk_window_set_resizable(GTK_WINDOW(alterar), FALSE);
  
  caixa=gtk_vbox_new(TRUE,30);
  gtk_container_add(GTK_CONTAINER(alterar),caixa);
  a_s=gtk_adjustment_new(1,1e-8, 1.5, 1e-2, 0, 0);
  a_a=gtk_adjustment_new(1,1e-8,1, 1e-4, 0, 0);
  a_t=gtk_adjustment_new(10,1, 13, 0.5, 0, 0);
  s_s=gtk_hscale_new(GTK_ADJUSTMENT(a_s));
  s_a=gtk_hscale_new(GTK_ADJUSTMENT(a_a));
  s_t=gtk_hscale_new(GTK_ADJUSTMENT(a_t));
  
  l_s=gtk_label_new("Escala da velocidade");
  l_a=gtk_label_new("Escala da aceleracao");
  l_t=gtk_label_new("Escala do tempo");
  
  gtk_box_pack_start(GTK_BOX(caixa),l_s,FALSE,FALSE,0);
  gtk_box_pack_start(GTK_BOX(caixa),s_s,FALSE,FALSE,0);
  gtk_box_pack_start(GTK_BOX(caixa),l_a,FALSE,FALSE,0);
  gtk_box_pack_start(GTK_BOX(caixa),s_a,FALSE,FALSE,0);
  gtk_box_pack_start(GTK_BOX(caixa),l_t,FALSE,FALSE,0);
  gtk_box_pack_start(GTK_BOX(caixa),s_t,FALSE,FALSE,0);
  
  //MENU
  vbox = gtk_vbox_new(FALSE, 0);
  gtk_container_add(GTK_CONTAINER(screen), vbox);
  menubar = gtk_menu_bar_new();
  
  filemenu = gtk_menu_new();
  opcoes = gtk_menu_item_new_with_label("Opcoes");
  about = gtk_menu_item_new_with_label("About");
  instrucoes = gtk_menu_item_new_with_label("Instrucoes");
  fechar = gtk_menu_item_new_with_label("Fechar");
  abrir = gtk_menu_item_new_with_label("Graficos v(t) e a(t)");
  new_point = gtk_menu_item_new_with_label("Guardar estado");
  recover_point = gtk_menu_item_new_with_label("Recuperar estado");
  escala_g=gtk_menu_item_new_with_label("Alterar escala");
  
  gtk_menu_item_set_submenu(GTK_MENU_ITEM(opcoes), filemenu);
  gtk_menu_shell_append(GTK_MENU_SHELL(filemenu), about);
  gtk_menu_shell_append(GTK_MENU_SHELL(filemenu), instrucoes);
  gtk_menu_shell_append(GTK_MENU_SHELL(filemenu), abrir);
  gtk_menu_shell_append(GTK_MENU_SHELL(filemenu), escala_g);
  gtk_menu_shell_append(GTK_MENU_SHELL(filemenu), new_point);
  gtk_menu_shell_append(GTK_MENU_SHELL(filemenu), recover_point);
  gtk_menu_shell_append(GTK_MENU_SHELL(filemenu), fechar);
  gtk_menu_shell_append(GTK_MENU_SHELL(menubar), opcoes);
  gtk_box_pack_start(GTK_BOX(vbox), menubar, FALSE, FALSE, 3);
	
  // Tabela
  tabela = gtk_table_new(22,10,TRUE);
  gtk_container_add(GTK_CONTAINER(vbox),tabela);
  gtk_table_set_row_spacings(GTK_TABLE(tabela), 2);
  gtk_table_set_col_spacings(GTK_TABLE(tabela), 2);

 	// labels de vel e acel
  v_label=gtk_label_new("Velocidade: 0");
  a_label=gtk_label_new("Aceleracao: 0");
  
 
  //CAIXA
  campo = gtk_hbox_new (TRUE, 0);
	
	
  //BOTOES
  demo=gtk_button_new_with_label("Demo");
  random=gtk_button_new_with_label("Random");
  pausa = gtk_button_new_with_label("Iniciar");
  reset = gtk_button_new_with_label("Reset");
  compute=gtk_button_new_with_label("Calcular");
  
  fronteira=gtk_check_button_new_with_label("fronteiras");
  gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(fronteira),TRUE);
  
  rasto=gtk_check_button_new_with_label("rasto");
  gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(rasto),TRUE);
  
  timer=gtk_label_new("Tempo: 0.0 s");
	texto=gtk_label_new("Controlos numericos de carga");
	erro=gtk_label_new("Nenhum erro");
	res=gtk_label_new(" ");
  
  //FRAMES
  frame_massa = gtk_frame_new("Massa/Raio");
  gtk_frame_set_shadow_type(GTK_FRAME(frame_massa), GTK_SHADOW_IN);
  
  frame_carga = gtk_frame_new("Cargas");
  gtk_frame_set_shadow_type(GTK_FRAME(frame_carga), GTK_SHADOW_IN);
 
  frame_vinicial = gtk_frame_new("Velocidades");
  gtk_frame_set_shadow_type(GTK_FRAME(frame_vinicial), GTK_SHADOW_IN);

  //IMAGENS
  preto = gtk_image_new_from_file("images/preto.png");
  vermelho = gtk_image_new_from_file("images/vermelho.png");
  verde = gtk_image_new_from_file("images/verde.png");
  azul = gtk_image_new_from_file("images/azul.png");

  //COMBOBOX E ENTRADAS
  combo = gtk_combo_box_new_text();
  gtk_combo_box_append_text(GTK_COMBO_BOX(combo), "Carga");
  gtk_combo_box_append_text(GTK_COMBO_BOX(combo), "Massa/Raio");
  gtk_combo_box_append_text(GTK_COMBO_BOX(combo), "V X");
  gtk_combo_box_append_text(GTK_COMBO_BOX(combo), "V Y");
  gtk_combo_box_append_text(GTK_COMBO_BOX(combo), "POS X");
  gtk_combo_box_append_text(GTK_COMBO_BOX(combo), "POS Y");
  

  entry[0] = gtk_entry_new();
  entry[1] = gtk_entry_new();
  entry[2] = gtk_entry_new();
  entry[3] = gtk_entry_new();


  //attach
  gtk_table_attach_defaults(GTK_TABLE(tabela), campo, 0, 6, 1, 9);
 	
  gtk_table_attach_defaults(GTK_TABLE(tabela), timer, 2,4,21,22);
  gtk_table_attach_defaults(GTK_TABLE(tabela), rasto, 5,6,21,22);
  gtk_table_attach_defaults(GTK_TABLE(tabela), pausa, 2, 3, 20, 21);
  gtk_table_attach_defaults(GTK_TABLE(tabela), reset, 3, 4, 20, 21);
  gtk_table_attach_defaults(GTK_TABLE(tabela), random, 4, 5, 20, 21);
  gtk_table_attach_defaults(GTK_TABLE(tabela), demo, 1, 2, 20, 21);
  
  gtk_table_attach_defaults(GTK_TABLE(tabela), frame_carga, 6, 10, 0, 7);
  gtk_table_attach_defaults(GTK_TABLE(tabela), frame_massa, 6, 10, 7, 12);
  gtk_table_attach_defaults(GTK_TABLE(tabela), frame_vinicial, 6, 10, 12, 17);
  
  
  gtk_table_attach_defaults(GTK_TABLE(tabela),texto,6,8,17,18);
  gtk_table_attach_defaults(GTK_TABLE(tabela), combo, 8,10,17,18);
  gtk_table_attach_defaults(GTK_TABLE(tabela), compute, 8,9,19,20);
  gtk_table_attach_defaults(GTK_TABLE(tabela), fronteira, 8,9,18,19);
  gtk_table_attach_defaults(GTK_TABLE(tabela), res, 7,9,20,21);
  gtk_table_attach_defaults(GTK_TABLE(tabela), erro, 7,9,21,22);

  gtk_table_attach_defaults(GTK_TABLE(tabela), entry[0], 9,10, 18, 19);
  gtk_table_attach_defaults(GTK_TABLE(tabela), entry[1], 9,10, 19, 20);
  gtk_table_attach_defaults(GTK_TABLE(tabela), entry[2], 9,10, 20, 21);
  gtk_table_attach_defaults(GTK_TABLE(tabela), entry[3], 9,10, 21, 22);
  
	gtk_table_attach_defaults(GTK_TABLE(tabela), preto, 6, 8, 18, 19);
  radio[0]=gtk_radio_button_new_with_label (NULL, "Carga q0"); 
  gtk_table_attach_defaults(GTK_TABLE(tabela),radio[0],6,8,18,19);
  
  gtk_table_attach_defaults(GTK_TABLE(tabela), verde, 6, 8, 19, 20);
  radio[1]=gtk_radio_button_new_with_label_from_widget (GTK_RADIO_BUTTON (radio[0]),"Carga Q1");  
  gtk_table_attach_defaults(GTK_TABLE(tabela),radio[1],6,8,19,20);

  gtk_table_attach_defaults(GTK_TABLE(tabela), vermelho, 6, 8, 20, 21);
  radio[2]=gtk_radio_button_new_with_label_from_widget (GTK_RADIO_BUTTON (radio[0]),"Carga Q2");  
  gtk_table_attach_defaults(GTK_TABLE(tabela),radio[2],6,8,20,21);

  gtk_table_attach_defaults(GTK_TABLE(tabela), azul, 6, 8, 21, 22);
  radio[3]=gtk_radio_button_new_with_label_from_widget (GTK_RADIO_BUTTON (radio[0]),"Carga Q3");  
  gtk_table_attach_defaults(GTK_TABLE(tabela),radio[3],6,8,21,22);
  
	gtk_toggle_button_set_active (GTK_TOGGLE_BUTTON (radio[1]), TRUE);

  //SLIDERS CARGA

  for(i=0,k=0; i<2;i++)
    {
      for(j=0; j<2; j++)
				{
	  			def_carga[k] = gtk_adjustment_new(0., -50., 50., 0.5, 0., 0.);  
	  			controlo_carga[k] = gtk_hscale_new(GTK_ADJUSTMENT(def_carga[k]));

	  			gtk_table_attach_defaults(GTK_TABLE(tabela), controlo_carga[k], 6+2*j, 8+2*j, 1+3*i,4+3*i); 
	  			gtk_scale_set_value_pos(GTK_SCALE(controlo_carga[k]), GTK_POS_LEFT);
	  			gtk_scale_add_mark(GTK_SCALE(controlo_carga[k]),0,GTK_POS_TOP,"0");

	  			q[k].qt = (double) gtk_range_get_value(GTK_RANGE(controlo_carga[k]));
	  
      		legenda_carga[k]=gtk_label_new(q[k].name);
      
	  			gtk_table_attach_defaults(GTK_TABLE(tabela),legenda_carga[k],6+2*j, 8+2*j, 3*i,3+3*i);
	  			k++;
				}
   }
  
  //SLIDERS MASSA

  for(i=0,k=0; i<2;i++)
    {
      for(j=0; j<2; j++)
				{
	  			def_massa[k] = gtk_adjustment_new(15, 5, 25, 1, 0, 0);
	  			controlo_massa[k] = gtk_hscale_new(GTK_ADJUSTMENT(def_massa[k]));

	  			gtk_table_attach_defaults(GTK_TABLE(tabela), controlo_massa[k], 6+2*j, 8+2*j, 9+2*i,10+2*i); 
	  			gtk_scale_set_value_pos(GTK_SCALE(controlo_massa[k]), GTK_POS_LEFT);
	  			q[k].mass = (double) gtk_range_get_value(GTK_RANGE(controlo_massa[k]));
      
				  legenda_massa[k]=gtk_label_new(q[k].name);
      
				  gtk_table_attach_defaults(GTK_TABLE(tabela),legenda_massa[k],6+2*j,8+2*j,8+i*2,9+i*2);
	  			k++;
				}
    }

  //SLIDERS V_INICIAL

  def_vinicial[0] = gtk_adjustment_new(0,-500, 500, 20, 0, 0);
  def_vinicial[1] = gtk_adjustment_new(0, -500,500, 20, 0, 0);
  controlo_vinicial[0] = gtk_hscale_new(GTK_ADJUSTMENT(def_vinicial[0]));
  controlo_vinicial[1] = gtk_hscale_new(GTK_ADJUSTMENT(def_vinicial[1]));
  
  gtk_table_attach_defaults(GTK_TABLE(tabela), controlo_vinicial[0], 6, 8, 14,16); 
  gtk_scale_set_value_pos(GTK_SCALE(controlo_vinicial[0]), GTK_POS_LEFT);
	gtk_scale_add_mark(GTK_SCALE(controlo_vinicial[0]),0,GTK_POS_TOP,"0");
  gtk_table_attach_defaults(GTK_TABLE(tabela), controlo_vinicial[1], 8, 10, 14,16); 
  gtk_scale_set_value_pos(GTK_SCALE(controlo_vinicial[1]), GTK_POS_LEFT);
	gtk_scale_add_mark(GTK_SCALE(controlo_vinicial[1]),0,GTK_POS_TOP,"0");
      
  q[0].vel.x = (double) gtk_range_get_value(GTK_RANGE(controlo_vinicial[0]));
  q[0].vel.y = (double) gtk_range_get_value(GTK_RANGE(controlo_vinicial[1]));
  
  legenda_vinicial[0] = gtk_label_new("Velocidade X");
  legenda_vinicial[1] = gtk_label_new("Velocidade Y");
  
  gtk_table_attach_defaults(GTK_TABLE(tabela),legenda_vinicial[0],6,8,13,14);
  gtk_table_attach_defaults(GTK_TABLE(tabela),legenda_vinicial[1],8,10,13,14);
 
  //-----------------Events and callbacks-------------------
  
	gtk_widget_add_events (screen, GDK_BUTTON_PRESS_MASK);
 	g_signal_connect (screen, "expose-event", G_CALLBACK(on_expose_event), NULL);
	//Funcionamento do menu
	g_signal_connect(G_OBJECT(about), "activate", G_CALLBACK(show_about), screen);
	g_signal_connect(G_OBJECT(fechar), "activate", G_CALLBACK(Teste_BotaoSair), screen);
	g_signal_connect(G_OBJECT(abrir), "activate", G_CALLBACK(abrir_grafico), (gpointer) 1);
	g_signal_connect(G_OBJECT(escala_g), "activate", G_CALLBACK(change_scale), (gpointer) 1);
	g_signal_connect(G_OBJECT(instrucoes), "activate", G_CALLBACK(show_instructions), screen);
	g_signal_connect(G_OBJECT(new_point), "activate", G_CALLBACK(save_point), screen);
	g_signal_connect(G_OBJECT(recover_point), "activate", G_CALLBACK(get_point), NULL);
  
  //tratamento do fecho das janelas
  g_signal_connect (G_OBJECT (screen), "delete_event", G_CALLBACK (Teste_DeleteEvent), screen);
  g_signal_connect (G_OBJECT (graph), "delete_event", G_CALLBACK (gtk_widget_hide_on_delete), (gpointer) 0);
  g_signal_connect (G_OBJECT (alterar), "delete_event", G_CALLBACK (gtk_widget_hide_on_delete), (gpointer) 0);
	
  //FUNCIONAMENTO DOS SLIDERS DE CARGA
  g_signal_connect (G_OBJECT(controlo_carga[0]), "value-changed", G_CALLBACK(mudar_carga),(gpointer) 0);
  g_signal_connect (G_OBJECT(controlo_carga[1]), "value-changed", G_CALLBACK(mudar_carga),(gpointer) 1);
  g_signal_connect (G_OBJECT(controlo_carga[2]), "value-changed", G_CALLBACK(mudar_carga),(gpointer) 2);
  g_signal_connect (G_OBJECT(controlo_carga[3]), "value-changed", G_CALLBACK(mudar_carga),(gpointer) 3);

  //FUNCIONAMENTO DOS SLIDERS DE MASSA
  g_signal_connect (G_OBJECT(controlo_massa[0]), "value-changed", G_CALLBACK(mudar_massa),(gpointer) 0);
  g_signal_connect (G_OBJECT(controlo_massa[1]), "value-changed", G_CALLBACK(mudar_massa),(gpointer) 1);
  g_signal_connect (G_OBJECT(controlo_massa[2]), "value-changed", G_CALLBACK(mudar_massa),(gpointer) 2);
  g_signal_connect (G_OBJECT(controlo_massa[3]), "value-changed", G_CALLBACK(mudar_massa),(gpointer) 3);


  //FUNCIONAMENTO DOS SLIDERS DE VELOCIDADE
 	g_signal_connect (G_OBJECT(controlo_vinicial[0]), "value-changed", G_CALLBACK(mudar_vel_x),NULL);
 	g_signal_connect (G_OBJECT(controlo_vinicial[1]), "value-changed", G_CALLBACK(mudar_vel_y),NULL);

	//FUNCIONAMENTO DOS SLIDERS DA ESCALA
	g_signal_connect (G_OBJECT(s_s), "value-changed", G_CALLBACK(valor_escala),(gpointer) 1);
	g_signal_connect (G_OBJECT(s_a), "value-changed", G_CALLBACK(valor_escala),(gpointer) 2);
	g_signal_connect (G_OBJECT(s_t), "value-changed", G_CALLBACK(valor_escala),(gpointer) 3);

  // FUNCIONAMENTO DOS RADIO BUTTONS
  g_signal_connect (G_OBJECT(radio[0]), "toggled", G_CALLBACK(radio_change),(gpointer) 0);
  g_signal_connect (G_OBJECT(radio[1]), "toggled", G_CALLBACK(radio_change),(gpointer) 1);
  g_signal_connect (G_OBJECT(radio[2]), "toggled", G_CALLBACK(radio_change),(gpointer) 2);
  g_signal_connect (G_OBJECT(radio[3]), "toggled", G_CALLBACK(radio_change),(gpointer) 3);
  
  // Posicionamento das cargas
 	g_signal_connect(screen, "button-press-event", G_CALLBACK(clicked), NULL);

 	//FUNCIONAMENTO DOS BOTOES
	g_signal_connect(G_OBJECT (pausa), "clicked", G_CALLBACK (tempo), NULL);
	g_signal_connect(G_OBJECT (reset), "clicked", G_CALLBACK (limpa), NULL);
	g_signal_connect(G_OBJECT (fronteira), "toggled", G_CALLBACK (border), NULL);
	g_signal_connect(G_OBJECT (rasto), "toggled", G_CALLBACK (set_trail), NULL);
	g_signal_connect(G_OBJECT (demo), "clicked", G_CALLBACK (apply_demo), NULL);
 	g_signal_connect(G_OBJECT (random), "clicked", G_CALLBACK (apply_random), NULL);

	
	//COMBOBOX
	g_signal_connect(G_OBJECT (compute),"clicked",G_CALLBACK (calcular),NULL);
	g_signal_connect(G_OBJECT(combo),"changed",G_CALLBACK(cleared),NULL);
	
	//signals do plot
  gtk_widget_add_events (graph, GDK_BUTTON_PRESS_MASK);
  
  g_signal_connect (graph, "expose-event", G_CALLBACK(plot), NULL); 
	
	//TIMEOUT (refresh rate)
  g_timeout_add (10, (GSourceFunc) time_handler, (gpointer) screen); 
  
  gtk_widget_show_all(screen);
  
  
  gtk_main ();
  return 0;
}

