from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q

import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
from scipy.interpolate import UnivariateSpline
from cStringIO import StringIO
import os
from base64 import b64encode


from wsoptimize.forms import CharacterForm, SkillForm, ClassTypeForm, DisplayForm, BuffsAssaultAlliesForm
from wsoptimize.models import SkillsData, ClassesData, CharacterData, BuffsAssaultAlliesData
from optimize.optimize import optimize_all

CALCULATE_URL = '/calculate'
DISPLAY_URL = '/display'
BUFFS_URL = '/buffs'

def graph(x, x2, y, xmax=0, ymax=0, string='', savefile=0, title=''):
	fig, ax1 = plt.subplots()
	fig.set_facecolor('white')
	fig.suptitle(title, fontsize=24, x=0.08)
	ax2 = ax1.twiny()
	for item in [fig, ax1, ax2]:
		item.patch.set_visible(False)
	
	ax1.spines["top"].set_visible(False)    
	ax1.spines["right"].set_visible(False)  
	ax1.get_xaxis().tick_bottom()  
	ax1.get_yaxis().tick_left()

	xx = np.linspace(min(x), max(x),1000)
	f = UnivariateSpline(x, y)

	ax1.plot(xx, f(xx), '#444444', linewidth=3)
	ax1.plot(xmax, f(np.float(xmax)), color='#005f5f', marker='h', linewidth=20 )

	ax1.set_xlim(min(x), max(x))
	ax2.set_xlim(np.min(x2), np.max(x2))
	ax1.set_ylim([np.min(y), np.max(y)+5])
	ax2.invert_xaxis()

	# labels
	ax1.set_xlabel('Power (AP/SP)', fontsize=14)
	ax1.set_ylabel("Expected Average Damage", fontsize=14)
	ax2.set_xlabel('Critical Chance', fontsize=14)
	buff = StringIO()
	canvas = FigureCanvas(fig)
	canvas.print_png(buff)
	# pil_image = PIL.Image.fromstring('RGB', canvas.get_width_height(), 
	# 			 canvas.tostring_rgb())
	# pil_image.save(buff, 'PNG')
	plt.cla()
	plt.clf()
	plt.close('all')
	imageinline = b64encode(buff.getvalue())
	buff.close()
	return imageinline
	
def display(request):
	
	display_data = DisplayForm()
	if request.method == 'POST':
		skillselect = request.POST['SkillName']
		rdata = display_data._load()
		print skillselect
		for row in rdata:
			if skillselect == row['name']:
				d = row
		display_image = graph(d['x1'], d['x2'], d['y'], d['ap_o'], d['dmg_o'])


		return render(request, 'display.html', {
			'display_form': display_data,
			'display_image': display_image,
			})

	else:
		transparent_image = 'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
		return render(request, 'display.html', {
				'display_form': display_data,
				'display_image': transparent_image,
				})


def calculate_form(request):

	# load info from data base
	class_types = [ i.classtype for i in ClassesData.objects.all()]
		# character info
	default = CharacterData.objects.filter(id=1).get()
	cdata = [{'pwr': default.pwr, 'chc':default.chc, 'chs':default.chs, 'pts':default.pts,
			'mpwr':default.pwr_mod, 'mdmg': default.dmg_mod, 'mchc': default.chc_mod, 'mchs': default.chs_mod 
		}]
	cdata[0]['modified_pwr'] = (float(default.pwr_mod)+1) * float(default.pwr)
	cdata[0]['modified_chc'] = float(default.chc_mod) + float(default.chc)/100
	cdata[0]['modified_chs'] = float(default.chs_mod) + float(default.chs)/100

		# skill info
	filterargs = {'wsclass':default.classtype, 'wstype':default.asp.lower()}
	skill_relations = SkillsData.objects.filter(**filterargs)

	sid = [i.id for i in skill_relations]
	names = [i.name for i in skill_relations]
	weights = [i.weight for i in skill_relations]
	tiers = [i.tier for i in skill_relations]
	analyze = [i.analyze for i in skill_relations]
	skills = [{'n':i[0], 'w':i[1], 't':i[2], 'a':i[3]} for i in zip(names, weights, tiers, analyze)]
	

	# user input data
	if request.method == 'POST':
		try:
			calculate_io = int(request.POST['OnCalculate'])
		except: 
			calculate_io = -1

		if calculate_io == 1:
			# saveing the data on enter
			c = [{i: request.POST.get(i) for i in cdata[0].keys()}]
			c[0]['mpwr'] = default.pwr_mod
			c[0]['mdmg'] = default.dmg_mod
			c[0]['mchc'] = default.chc_mod
			c[0]['mchs'] = default.chs_mod
			c[0]['modified_pwr'] = (float(default.pwr_mod)+1) * float(default.pwr)
			c[0]['modified_chc'] = float(default.chc_mod) + float(default.chc)/100
			c[0]['modified_chs'] = float(default.chs_mod) + float(default.chs)/100

			character_form = CharacterForm(cdata=c)

				# skill relationship info
			w = request.POST.getlist('w')
			t = request.POST.getlist('t')
			a = request.POST.getlist('a')

			skills = [{'n':i[0], 'w':i[1], 't':i[2], 'a':i[3]} for i in zip(names, w, t, a)]
			skill_form = SkillForm(skills=skills)
			# validation
			cvalidate = character_form._validate()
			svalidate = skill_form._validate()
			if cvalidate:
				character_form._save(cid=default.id, classtype=default.classtype, asp=default.asp)
			
			if svalidate:				
				skill_form._save(sid, w, t, a)

			return HttpResponseRedirect('/calculate')

		elif calculate_io == 0:
			if not skills:
				return HttpResponseRedirect('/')
			# Save Form Instances with request.POST data
				# character info
			c = [{i: request.POST.get(i) for i in cdata[0].keys()}]
			c[0]['mpwr'] = default.pwr_mod
			c[0]['mdmg'] = default.dmg_mod
			c[0]['mchc'] = default.chc_mod
			c[0]['mchs'] = default.chs_mod
			c[0]['modified_pwr'] = (float(default.pwr_mod)+1) * float(default.pwr)
			c[0]['modified_chc'] = float(default.chc_mod) + float(default.chc)/100
			c[0]['modified_chs'] = float(default.chs_mod) + float(default.chs)/100

			character_form = CharacterForm(cdata=c)

				# skill relationship info
			w = request.POST.getlist('w')
			t = request.POST.getlist('t')
			a = request.POST.getlist('a')

			skills = [{'n':i[0], 'w':i[1], 't':i[2], 'a':i[3]} for i in zip(names, w, t, a)]
			skill_form = SkillForm(skills=skills)
			# validation
			cvalidate = character_form._validate()
			svalidate = skill_form._validate()
			if cvalidate:
				character_form._save(cid=default.id, classtype=default.classtype, asp=default.asp)
			
			if svalidate:				
				skill_form._save(sid, w, t, a)

			if cvalidate and svalidate:
				cdata = character_form.cdata[0]
				# cdata = [character_form.cdata[0][i] for i in character_form.cdata[0].keys() ]
				cdata = [float(character_form.cdata[0]['pwr']),
					float(character_form.cdata[0]['chc'])/100,
					float(character_form.cdata[0]['chs'])/100,
					float(character_form.cdata[0]['pts']),
					]
				sb = [i.slope for i in skill_relations]
				cb = [i.constant for i in skill_relations]
				st = [i.slope_tier for i in skill_relations]
				ct = [i.constant_tier for i in skill_relations]
				nhits = [i.nhits for i in skill_relations]
				# names, w, t, a
				sdata = []
				for b, c, d, e, f, g, h, j, i in zip(names, sb, cb, st, ct, t, w, nhits, a):
					if not int(i): continue
					sdata += [[b.encode('ascii', 'ignore'), c, d, e, f, g, h, j]]

					# bdata
				bdata = [default.dmg_mod, default.pwr_mod, default.chc_mod, default.chs_mod]
				rdata = optimize_all(cdata, sdata, bdata)
				#modify return data
				for i, row in enumerate(rdata):
					rdata[i]['name'] = row['name']
					rdata[i]['ap_o'] = int(round(row['ap_o']))
					rdata[i]['cc_o'] = round(row['cc_o'], 2)
					rdata[i]['dmg_o'] = round(row['dmg_o'])
				#store data
				display_data = DisplayForm(data=rdata)
				display_data._save()

				return HttpResponseRedirect('/display')

		elif 'ClassSelectType' in request.POST:
			default_class = request.POST['ClassSelectType']
			default.classtype = default_class
			default.save()
			class_type_form = ClassTypeForm(class_types=class_types, default_class=default_class)

			return HttpResponseRedirect('/',
				{
				'class_type_form': class_type_form,
				})

		elif 'apspSelect' in request.POST:
			apsp_select = request.POST['apspSelect']
			if apsp_select == 'Assault':
				default.asp = 'Support'
			else:
				default.asp = 'Assault'
			default.save()

			return HttpResponseRedirect('/',
				{
				'apsp_option': default.asp,
				})

		else:
			return HttpResponseRedirect('/')
			
	else:
		character_form = CharacterForm(cdata=cdata)
		class_type_form = ClassTypeForm(class_types=class_types, default_class=default.classtype)
		skill_form = SkillForm(skills=skills)

		return render(request, 'calculate_form.html', {
			'character_form': character_form, 
			'class_type_form': class_type_form,
			'skill_form': skill_form,
			'apsp_option': default.asp,
			})


def buffs_form(request):
	# load info from data base
	class_types = [ i.classtype for i in ClassesData.objects.all()]
		# character info
	default = CharacterData.objects.filter(id=1).get()
	cdata = [{'pwr': default.pwr, 'chc':default.chc, 'chs':default.chs, 'pts':default.pts,
			'mpwr':default.pwr_mod, 'mdmg': default.dmg_mod, 'mchc': default.chc_mod, 'mchs': default.chs_mod 
		}]
		# buffs info
	buffs_data = BuffsAssaultAlliesData.objects.filter(Q(Target='all')|Q(Target=default.classtype))

	bid = [i.id for i in buffs_data]
	n = [i.Name for i in buffs_data]
	t = [i.Target for i in buffs_data]
	e = [i.Effect for i in buffs_data]
	mt = [i.Type for i in buffs_data]
	u = [i.Uptime for i in buffs_data]
	m = [i.Modifier for i in buffs_data]
	a = [i.Analyze for i in buffs_data]
	buffs = [{'n':i[0], 't':i[1], 'e':i[2], 'mt':i[3], 'u':i[4], 'm':i[5], 'a':i[6]}
	 for i in zip(n, t, e, mt, u, m, a)]


	if request.method == 'POST':
		if 'onBuffsSave' in request.POST:
			# validate
			e = request.POST.getlist('Effect')
			u = request.POST.getlist('Uptime')
			a = request.POST.getlist('Analyze')
			

			buffs = [{'n':i[0], 't':i[1], 'e':i[2], 'mt':i[3], 'u':i[4], 'm':i[5], 'a':i[6]}
			 for i in zip(n, t, e, mt, u, m, a)]

			buffs_form = BuffsAssaultAlliesForm(buffs=buffs)

			if buffs_form._validate():
				# calculations:
				mpwr = []
				mchc = []
				mdmg = []
				mchs = []
				for i, row in enumerate(buffs):
					if float(row['e']) > 1:
						buffs[i]['m'] = float(row['e'])/float(default.pwr)*float(row['u'])
					else:
						buffs[i]['m'] = float(row['e'])*float(row['u'])
					# row['m'] = float(row['e'])*float(row['u'])
					if int(row['a']):
						if row['mt'] == 'Dmg':
							mdmg += [row['m']]
						elif row['mt'] == 'Pwr':
							mpwr += [row['m']]
						elif row['mt'] == 'Chr':
							mchc += [row['m']]
						elif row['mt'] == 'Chs':
							mchs += [row['m']]

				# assume additive
				cdata[0]['mpwr'] = np.sum(mpwr)
				cdata[0]['mdmg'] = np.sum(mdmg)
				cdata[0]['mchc'] = np.sum(mchc)
				cdata[0]['mchs'] = np.sum(mchs)

				character_form = CharacterForm(cdata=cdata)
				if character_form._validate():
					character_form._save(1, default.classtype, default.asp)
				# save data
				buffs_form._save(bid, buffs)

				class_type_form = ClassTypeForm(class_types=class_types, default_class=default.classtype)
				return render(request, 'buffs_form.html', {
					'character_form': character_form,
					'class_type_form': class_type_form,
					'buffs_form': buffs_form,
					'apsp_option': default.asp,
					})

		elif 'ClassSelectType' in request.POST:
			default_class = request.POST['ClassSelectType']
			default.classtype = default_class
			default.save()
			class_type_form = ClassTypeForm(class_types=class_types, default_class=default_class)

			return HttpResponseRedirect('/buffs')

		elif 'apspSelect' in request.POST:
			apsp_select = request.POST['apspSelect']
			if apsp_select == 'Assault':
				default.asp = 'Support'
			else:
				default.asp = 'Assault'
			default.save()

			return HttpResponseRedirect('/buffs')

		else:
			return HttpResponseRedirect('/buffs')

	buffs_form = BuffsAssaultAlliesForm(buffs=buffs)
	character_form = CharacterForm(cdata=cdata)
	class_type_form = ClassTypeForm(class_types=class_types, default_class=default.classtype)
	
	return render(request, 'buffs_form.html', {
		'character_form': character_form,
		'class_type_form': class_type_form,
		'buffs_form': buffs_form,
		'apsp_option': default.asp,
		})