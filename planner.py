# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 01:07:31 2024

@author: kevinh
"""

from copy import deepcopy

class Course:
    def __init__(self, fac, num, name="?"):
        self.fac = fac
        self.name = name
        
        if type(num) == list:
            self.rng = num
            self.typ = "crsrng"
        else:
            self.num = num
            self.typ = "crs"
            
        self.code = fac + str(num)
        
# (Num (anyof Str Course Prereq))
class Prereq:
    def __init__(self, amt, subreqs):
        self.amt = amt
        self.subreqs = subreqs
        self.typ = "prq"
            
# (Course ReqTree)
class CourseReq:
    def __init__(self, crs, reqs):
        self.crs = crs
        self.reqs = reqs
        self.typ = "creq"
        
# (Str (listof CourseReq or ReqTree))
class ReqTree:
    def __init__(self, op, subreqs, ovlp_allowed=False):
        self.op = op
        self.subreqs = subreqs
        self.typ = "reqt"
        self.ovlp_allowed = ovlp_allowed
        
        
def str_to_course(s):
    for i in range(len(s)):
        if 48 <= ord(s[i]) <= 57:
            try:
                n = int(s[i:])
            except ValueError:
                n = s[i:]
                
            return Course(s[:i], n)
        
req_dict = {
    # Enter prereqs
    # e.g. "CRS105": "(+ (* CRS101 CRS102) CRS104)"
}

power_dict = {}
i = 0
for c in req_dict:
    power_dict[c] = 2**i
    i += 1
    
found = {}

def course_to_coursereq(crs):
    global found
    
    if crs.code in found:
        return found[crs.code]
    
    # prereqs = input(crs.code)
    prereqs = req_dict[crs.code]
    
    if prereqs == "":
        found[crs.code] = CourseReq(crs, None)
        return CourseReq(crs, None)
    
    reqt = str_to_reqtree(prereqs)
    
    found[crs.code] = CourseReq(crs, reqt)
    return CourseReq(crs, reqt)
    
    
def str_to_reqtree(s):
    can_overlap = False
    
    if 49 <= ord(s[1]) <= 57:
        i = s.index(" ")
        if s[i-1] == "'":
            n = int(s[1 : i-1])
            s = "(*'" + f" (+ {s[i+1:]}"*n + ")"
        else:
            n = int(s[1 : i])
            s = "(*" + f" (+ {s[i+1:]}"*n + ")"
            
    s = s[1:-1]
    s += " "
    # print(s)
    if s[1] == "'":
        can_overlap = True
        start, end = 3, 3
    else:
        start, end = 2, 2
    
    subreqs = []
    
    while end < len(s):
        if s[end] == "(":
            start = end
            unmatched = 1
            
            while unmatched > 0:
                end += 1
                
                if s[end] == "(":
                    unmatched += 1
                elif s[end] == ")":
                    unmatched -= 1
                    
            subreqs.append(str_to_reqtree(s[start : end + 1]))
            
            end += 2
            start = end
            
        elif s[end] == " ":
            subreqs.append(course_to_coursereq(str_to_course(s[start : end])))
            
            end += 1
            start = end
            
        else:
            end += 1
    
    return ReqTree(s[0], subreqs, can_overlap)

# (make-way (listof (Course or Str)) (listof (Course or Str)))
class Way:
    def __init__(self, tot, used):
        self.tot = tot
        self.used = used
        
ways_found = {}

def all_ways_to_take(crsreq):
    global ways_found
    
    if crsreq.crs.code in ways_found:
        # return deepcopy(ways_found[crsreq.crs.code])
        ways_got = ways_found[crsreq.crs.code]
        return [Way(deepcopy(w), [w[-1]]) for w in ways_got]
    
    if crsreq.reqs == None:
        ways_found[crsreq.crs.code] = [[crsreq.crs]]
        # return [[crsreq.crs]]
        return [Way([crsreq.crs], crsreq.crs)]
    
    # listof Way
    all_ways = []
    
    if crsreq.reqs.op == "+":
        for subreq in crsreq.reqs.subreqs:
            # if subreq.typ == "creq":
            #     ways = all_ways_to_take(subreq)
            #     for way in ways:
            #         way.append(crsreq.crs)
                    
            #         for i in range(len(way)):
            #             if type(way[i]) != str:
            #                 way[i] = way[i].code
                            
            #         all_ways.append(way)
                    
            # else:
            #     ways = all_ways_to_take(CourseReq(subreq))
            #     for way in ways:
            #         for i in range(len(way)):
            #             if type(way[i]) != str:
            #                 way[i] = way[i].code
                            
            #         all_ways.append(way)
            
            # listof Way
            ways = all_subways(crsreq.crs, subreq)
            
            for way in ways:
                # to comment out, just shows course codes directly for debugging
                # for i in range(len(way)):
                #     if type(way[i]) != str:
                #         way[i] = way[i].code
                way = to_string(way)
                # to comment out, just shows...
                
                way.tot.append(crsreq.crs.code)
                # way.append(crsreq.crs.code)
                # way.append(crsreq.crs)
                all_ways.append(way)
                    
          
    # TODO: figure out and (*)
    else:
        # TODO: may not need
        # top_level = top_reqs(req_dict[crsreq.crs.code])
        
        curr_ways = all_subways(crsreq.crs, crsreq.reqs.subreqs[0])
        for i in range(1, len(crsreq.reqs.subreqs)):
            subreq = crsreq.reqs.subreqs[i]
            # prevreq = crsreq.reqs.subreqs[i-1]
            # TODO: figure out how to has compound
            
            new_ways = all_subways(crsreq.crs, subreq)
            temp_ways = []
            
            for curr_way in curr_ways:
                curr_way = to_string(curr_way)
                for new_way in new_ways:
                    new_way = to_string(new_way)
                    if not shared(new_way.used, curr_way.used) or crsreq.reqs.ovlp_allowed:# or new_way[-1] not in top_level:
                        new_used = deepcopy(curr_way.used)
                        new_used.append(new_way.tot[-1])
                        temp_ways.append(Way(union(deepcopy(curr_way.tot), deepcopy(new_way.tot)), new_used))
                    
            curr_ways = remove_dupes(sorted(temp_ways, key=sum_way))
            
        for way in curr_ways:
            way = to_string(way)
            
            # way.append(crsreq.crs.code)
            way.tot.append(crsreq.crs.code)
            # way.append(crsreq.crs)
            all_ways.append(way)
            
                    
    if crsreq.crs.code != placeholder.code:
        ways_found[crsreq.crs.code] = [w.tot for w in all_ways]
    return deepcopy(all_ways)

# def top_reqs(s):
#     ops = ["+", "*"]
#     for op in ops:
#         s = s.replace(f"({op} ", "")
#     return s.replace(")", "").split(" ")

placeholder = Course("XXX", 101)

def all_subways(crs, subreq):
    if subreq.typ == "creq":
        ways = all_ways_to_take(subreq)       
        for way in ways:
            way.used = [way.tot[-1]]
            
    else:
        # TODO: might not need update dict by crs anymo
        # req_dict[placeholder.code] = req_dict[crs.code]
        ways = all_ways_to_take(CourseReq(placeholder, subreq))
        # for way in ways:
        #     way.pop(-1)
        for way in ways:
            way.tot.pop(-1)
            
    # for way in ways:
    #     way.used = [way.tot[-1]]
            
    return ways
        
# def to_string(crslst):
#     for i in range(len(crslst)):
#         if type(crslst[i]) != str:
#             crslst[i] = crslst[i].code
            
#     return crslst
def to_string(way):
    t = deepcopy(way.tot)
    u = deepcopy(way.used)
    
    for lst in [t, u]:
        for i in range(len(lst)):
            if type(lst[i]) != str:
                lst[i] = lst[i].code
            
    return Way(t, u)
            
# def sum_way(way):
#     return sum([power_dict[c] for c in way])
def sum_way(way):
    return sum([power_dict[c] for c in way.tot])

def remove_dupes(ways):
    if len(ways) == 0:
        return ways
    
    new = [ways[0]]
    
    for i in range(1, len(ways)):
        if sum_way(ways[i]) != sum_way(ways[i-1]):
            new.append(ways[i])
            
    return new

def union(A, B):
    # hopefully can get union in O(n) maybe or O(nlogn)
    for b in B:
        if b not in A:
            A.append(b)
            
    return A #new


def shared(A, B):
    for b in B:
        if b in A:
            return True
        
    return False
            
# print(union([1,2,3,4,5,6], [3,4,5,6,7,8])) #new

# TODO: dupes for this case below
print([w.tot for w in sorted(all_ways_to_take(course_to_coursereq(Course("TEST", 101))), key=lambda x: len(x.tot))])
    
#TODO: test again
def check_prereq(pre, cand):
    n = pre.amt
    
    non = False
    
    if n == -1:
        non = True
    elif n == 0:
        return True
    
    for sub in pre.subreqs:
        if check_subreq(sub, cand):
            n -= 1
            if non:
                return False
            
        if n == 0:
            return True
        
    return False

def check_subreq(sub, cand):
    if type(sub) == str:
        return sub in [c.fac for c in cand]
    elif sub.typ == "crs":
        return sub.code in [c.code for c in cand]
    elif sub.typ == "crsrng":
        for c in cand:
            if sub.code == c.code and sub.rng[0] <= c.num <= sub.rng[1]:
                return True
        return False
    else:
        return check_prereq(sub, cand)

# print(all_ways_to_take(course_to_coursereq(Course("CS", 230))))
