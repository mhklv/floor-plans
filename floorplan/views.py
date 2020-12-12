from django.shortcuts import render
from .models import FloorPlan
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import View
from django.shortcuts import get_object_or_404

from .utils import ObjectDetailMixin
from .forms import PlanForm
from django.shortcuts import redirect


#import logic
from .logic.make_graph_houghlines import *

# Create your views here.

def plan_list(request):
    plans = FloorPlan.objects.all()
    return render(request, 'floorplan/index.html', context={'plans': plans})

def plan_detail(request):
    graph = FloorPlan.get_graph()
    return render(request, 'floorplan/plan_detail.html', context={'graph': graph})

def graph_create(plan):
        img = cv2.imread('media/'+ plan.get_image())
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        negative = cv2.bitwise_not(gray)

        thinned = ximgproc.thinning(negative)
        thinned = dilate(thinned)

        _, negative = cv2.threshold(negative, 50, 255, cv2.THRESH_BINARY)

        distance = cv2.distanceTransform(negative, cv2.DIST_L2, cv2.DIST_MASK_5)

        #delete when need
        cv2.imwrite('negative.png', negative)
        cv2.imwrite('thinned.png', thinned)
        cv2.imwrite('distance.png', distance)
        #

        lines_cleared_img = img.copy()
        lines_cleared_img[::] = 0

        lines_img = img.copy()
        lines_img[::] = 0

        lines = cv2.HoughLinesP(thinned, 1, np.pi / 2, 5, minLineLength=30, maxLineGap=0)

        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(lines_img, (x1, y1), (x2, y2), (0, 0, 255), 3)
        
        lines = remove_thin_lines(lines, distance, 2.1)

        walls_img = negative.copy()
        walls_img[::] = 0

        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(lines_cleared_img, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.rectangle(walls_img, (x1, y1), (x2, y2), 255, 35)

        img_height = walls_img.shape[0]
        img_width = walls_img.shape[1]

        verts = list()
        
        scale = 20

        if(img.shape[0] < 2000 | img.shape[1] < 2000):
            scale = 15


        if(img.shape[0] < 1000 | img.shape[1] < 1000):
            scale = 15

        
        c = 0
        for i in range(0, img_height, scale):
            for j in range(0, img_width, scale):
                x = j + scale // 4
                y = i + scale // 4
                verts.append(Vertice(c, x, y))
                c += 1
        

        graph = Graph(verts)
        connect_graph(graph, 100)
        cut_off_edges(walls_img, graph)
        graph = remove_free_vertices(graph)


        graph_outfile = open('media/'+ plan.get_image() + '.json', 'w')

        json_convert(graph, graph_outfile,'media/'+ plan.get_image())

        graph_outfile.close()

class PlanDetail(ObjectDetailMixin, View):
    model = FloorPlan
    
    template = 'floorplan/plan_detail.html'

class PlanCreate(View):
    def get(self, request):
        form = PlanForm
        return render(request, 'floorplan/plan_create.html', context={'form' : form})
    

    def post(self, request):
        bound_form = PlanForm(request.POST, request.FILES)
        
        if bound_form.is_valid():

            new_plan = bound_form.save()

            graph_create(new_plan)

            return redirect(new_plan)
        return render(request, 'floorplan/plan_create.html', context = {'form': bound_form})