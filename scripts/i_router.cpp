#include <vector>
#include <queue>
#include <fstream>
#include <iostream>
#include <cmath>
#include <algorithm>
#include <limits>
using namespace std;
int W,H,S,L; const double D=.05;
struct Shape{int kind,mask,net;double ax,ay,bx,by,r;};
struct Task{int id,mode,net,sl;double sx,sy;int tl;double tx,ty,w;};
vector<Shape>obs;vector<unsigned char>occ,vb;vector<int>g,par;
double dist(double x,double y,Shape a){if(a.kind==0)return hypot(max({a.ax-x,0.,x-a.bx}),max({a.ay-y,0.,y-a.by}));double dx=a.bx-a.ax,dy=a.by-a.ay,dd=dx*dx+dy*dy,t=dd?((x-a.ax)*dx+(y-a.ay)*dy)/dd:0;t=max(0.,min(1.,t));return hypot(x-a.ax-t*dx,y-a.ay-t*dy)-a.r;}
void build(Task t){fill(occ.begin(),occ.end(),0);fill(vb.begin(),vb.end(),0);double rr=t.w/2+.125+.04;for(auto a:obs){if(a.net==t.net)continue;double margin=max(rr,.375)+a.r;int x0=max(0,(int)floor((min(a.ax,a.bx)-margin)/D)),x1=min(W-1,(int)ceil((max(a.ax,a.bx)+margin)/D)),y0=max(0,(int)floor((min(a.ay,a.by)-margin)/D)),y1=min(H-1,(int)ceil((max(a.ay,a.by)+margin)/D));for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++){int n=y*W+x;double dd=dist(x*D,y*D,a);if(dd<=.375)vb[n]=1;if(dd<=rr)for(int l=0;l<L;l++)if(a.mask&(1<<l))occ[l*S+n]=1;}}}
struct Q{int f,c,n;bool operator<(Q const&o)const{return f>o.f;}};
int heur(int a,int en){int x=abs(a%W-en%W),y=abs(a/W-en/W);return 10*max(x,y)+4*min(x,y);}
vector<int>route(Task t){fill(g.begin(),g.end(),numeric_limits<int>::max());int st=t.sl*S+lround(t.sy/D)*W+lround(t.sx/D),goal=t.tl*S+lround(t.ty/D)*W+lround(t.tx/D);priority_queue<Q>q;g[st]=0;par[st]=-1;q.push({0,0,st});int dx[]={1,-1,0,0,1,1,-1,-1},dy[]={0,0,1,-1,1,-1,1,-1};int startxy=st%S;
while(!q.empty()){auto a=q.top();q.pop();if(a.c!=g[a.n])continue;int xy=a.n%S,la=a.n/S,x=xy%W,y=xy/W;bool end=(!t.mode&&a.n==goal)||(t.mode&&la==t.sl&&!vb[xy]&&hypot((x-startxy%W)*D,(y-startxy/W)*D)>.55&&x%2==0&&y%2==0);
if(end){vector<int>p;for(int j=a.n;j!=-1;j=par[j])p.push_back(j);reverse(p.begin(),p.end());return p;}
auto add=[&](int nn,int cost){if(cost<g[nn]){g[nn]=cost;par[nn]=a.n;q.push({cost+(t.mode?0:heur(nn%S,goal%S)),cost,nn});}};
for(int k=0;k<8;k++){int nx=x+dx[k],ny=y+dy[k];if(nx<11||nx>W-12||ny<11||ny>H-12)continue;int nn=la*S+ny*W+nx;if(occ[nn])continue;int cost=a.c+(k<4?10:14);if(par[a.n]>=0&&a.n-par[a.n]!=nn-a.n)cost++;add(nn,cost);}
if(!t.mode&&x%2==0&&y%2==0&&!vb[xy])for(int l=0;l<L;l++)if(l!=la&&!occ[l*S+xy])add(l*S+xy,a.c+240);
}return {};}
int main(int argc,char**argv){ifstream f(argv[1]);ofstream out(argv[2]);f>>W>>H>>L;S=W*H;occ.resize(S*L);vb.resize(S);g.resize(S*L);par.resize(S*L);int c;f>>c;for(int i=0;i<c;i++){Shape a;f>>a.kind>>a.mask>>a.net>>a.ax>>a.ay>>a.bx>>a.by>>a.r;obs.push_back(a);}f>>c;vector<Task>ts(c);for(auto&t:ts)f>>t.id>>t.mode>>t.net>>t.sl>>t.sx>>t.sy>>t.tl>>t.tx>>t.ty>>t.w;int done=0;
for(auto t:ts){build(t);auto path=route(t);if(path.empty()){cout<<"FAILED "<<t.id<<endl;continue;}vector<int>p{path.front()};for(size_t i=1;i+1<path.size();i++)if(path[i]-path[i-1]!=path[i+1]-path[i])p.push_back(path[i]);if(p.back()!=path.back())p.push_back(path.back());out<<t.id<<' '<<p.size();for(int a:p)out<<' '<<a/S<<' '<<(a%S)%W<<' '<<(a%S)/W;out<<'\n';out.flush();for(size_t i=1;i<p.size();i++){int a=p[i-1],z=p[i];if(a/S==z/S)obs.push_back({1,1<<(a/S),t.net,(a%S%W)*D,(a%S/W)*D,(z%S%W)*D,(z%S/W)*D,t.w/2});else obs.push_back({1,(1<<L)-1,t.net,(a%S%W)*D,(a%S/W)*D,(a%S%W)*D,(a%S/W)*D,.2});}if(t.mode){int xy=p.back()%S;obs.push_back({1,(1<<L)-1,t.net,(xy%W)*D,(xy/W)*D,(xy%W)*D,(xy/W)*D,.2});}done++;if(done%10==0)cout<<"ROUTED "<<done<<'/'<<c<<endl;}cout<<"DONE "<<done<<'/'<<c<<endl;return done==c?0:1;}
