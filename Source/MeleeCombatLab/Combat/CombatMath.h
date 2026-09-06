#pragma once
#include <algorithm>
#include <cmath>

namespace mcl
{
constexpr double Pi = 3.14159265358979323846;
constexpr double Rad = Pi / 180.;
inline double clamp(double v, double a, double b) { return std::clamp(v, a, b); }
inline double mix(double a, double b, double t) { return a + (b-a)*t; }
inline double smooth(double t) { t=clamp(t,0.,1.); return t*t*(3.-2.*t); }
inline double wrap(double a) { return std::remainder(a,360.); }
struct Vec
{
    double x=0,y=0,z=0;
    Vec operator+(Vec b) const { return {x+b.x,y+b.y,z+b.z}; }
    Vec operator-(Vec b) const { return {x-b.x,y-b.y,z-b.z}; }
    Vec operator*(double s) const { return {x*s,y*s,z*s}; }
    Vec operator/(double s) const { return *this*(1./s); }
    Vec& operator+=(Vec b) { *this=*this+b; return *this; }
    double dot(Vec b) const { return x*b.x+y*b.y+z*b.z; }
    Vec cross(Vec b) const { return {y*b.z-z*b.y,z*b.x-x*b.z,x*b.y-y*b.x}; }
    double length() const { return std::sqrt(dot(*this)); }
    Vec normal() const { return length()>1e-9 ? *this/length() : Vec{}; }
};
inline Vec lerp(Vec a,Vec b,double t) { return a+(b-a)*t; }
inline double angle(Vec a,Vec b) { return std::acos(clamp(a.normal().dot(b.normal()),-1.,1.))/Rad; }
// Spherical direction interpolation avoids length collapse through broad weapon arcs.
inline Vec slerp(Vec a,Vec b,double t)
{
    a=a.normal(); b=b.normal(); double d=clamp(a.dot(b),-1.,1.);
    if(d>.9995) return lerp(a,b,t).normal();
    if(d<-.9995) { Vec n=a.cross({0,0,1}); if(n.length()<.01)n=a.cross({0,1,0}); return a*std::cos(Pi*t)+n.normal()*std::sin(Pi*t); }
    double w=std::acos(d); return (a*std::sin((1-t)*w)+b*std::sin(t*w))/std::sin(w);
}
struct Orientation
{
    double yaw=0,pitch=0;
    Vec forward() const { return {std::cos(pitch*Rad)*std::cos(yaw*Rad),std::cos(pitch*Rad)*std::sin(yaw*Rad),std::sin(pitch*Rad)}; }
    Vec right() const { return {-std::sin(yaw*Rad),std::cos(yaw*Rad),0}; }
    Vec up() const { return forward().cross(right()); }
    Vec world(Vec v) const { return forward()*v.x+right()*v.y+up()*v.z; }
    Vec local(Vec v) const { return {v.dot(forward()),v.dot(right()),v.dot(up())}; }
};
inline Orientation approach(Orientation a,Orientation b,double yawRate,double pitchRate,double dt)
{
    return {wrap(a.yaw+clamp(wrap(b.yaw-a.yaw),-yawRate*dt,yawRate*dt)),
        clamp(a.pitch+clamp(b.pitch-a.pitch,-pitchRate*dt,pitchRate*dt),-85.,85.)};
}
struct Segment { Vec a,b; };
struct Pose { Vec hilt,tip; Segment blade() const { return {hilt,tip}; } };
inline double pointSegmentDistance(Vec p,Segment s)
{
    Vec d=s.b-s.a; double n=d.dot(d);
    return (p-(s.a+d*(n>1e-12?clamp((p-s.a).dot(d)/n,0.,1.):0.))).length();
}
inline double segmentDistance(Segment p,Segment q)
{
    Vec u=p.b-p.a,v=q.b-q.a,w=p.a-q.a;
    double a=u.dot(u),b=u.dot(v),c=v.dot(v),d=u.dot(w),e=v.dot(w);
    if(a<1e-10)return pointSegmentDistance(p.a,q);
    if(c<1e-10)return pointSegmentDistance(q.a,p);
    double den=a*c-b*b,s=den>1e-10?clamp((b*e-c*d)/den,0.,1.):0.;
    double t=(b*s+e)/c;
    if(t<0){t=0;s=clamp(-d/a,0.,1.);} else if(t>1){t=1;s=clamp((b-d)/a,0.,1.);}
    return (w+u*s-v*t).length();
}
inline bool segmentBox(Segment s,Vec center,Orientation rotation,Vec half,double radius=0)
{
    Vec a=rotation.local(s.a-center),b=rotation.local(s.b-center); double lo=0,hi=1;
    const double aa[]={a.x,a.y,a.z},bb[]={b.x,b.y,b.z},hh[]={half.x+radius,half.y+radius,half.z+radius};
    for(int i=0;i<3;++i){double d=bb[i]-aa[i];if(std::abs(d)<1e-10){if(std::abs(aa[i])>hh[i])return false;}
        else{double t0=(-hh[i]-aa[i])/d,t1=(hh[i]-aa[i])/d;if(t0>t1)std::swap(t0,t1);lo=std::max(lo,t0);hi=std::min(hi,t1);if(lo>hi)return false;}}
    return true;
}
// Intersect a swept point with a finite cone, inflated radially by blade thickness.
inline bool segmentCone(Segment s,Vec origin,Orientation rotation,double length,double halfAngle,double radius)
{
    Vec a=rotation.local(s.a-origin),d=rotation.local(s.b-s.a);
    double lo=0,hi=1;
    if(std::abs(d.x)<1e-10){if(a.x<0||a.x>length)return false;}
    else{double t0=-a.x/d.x,t1=(length-a.x)/d.x;if(t0>t1)std::swap(t0,t1);lo=std::max(lo,t0);hi=std::min(hi,t1);if(lo>hi)return false;}
    double k=std::tan(halfAngle*Rad),r=k*a.x+radius;
    double A=d.y*d.y+d.z*d.z-k*k*d.x*d.x;
    double B=2*(a.y*d.y+a.z*d.z-r*k*d.x),C=a.y*a.y+a.z*a.z-r*r;
    auto f=[&](double t){return A*t*t+B*t+C;};
    if(f(lo)<=0||f(hi)<=0)return true;
    return A>1e-12 && -B/(2*A)>lo && -B/(2*A)<hi && f(-B/(2*A))<=0;
}
}
