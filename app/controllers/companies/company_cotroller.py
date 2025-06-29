from flask import Blueprint,request,jsonify
from app.status_codes import HTTP_400_BAD_REQUEST,HTTP_409_CONFLICT,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_200_OK,HTTP_404_NOT_FOUND,HTTP_403_FORBIDDEN
import validators
from app.models.companies import Company
from app.models.users import User
from app.extentions import db,bcrypt
from flask_jwt_extended import create_access_token,create_refresh_token,jwt_required,get_jwt_identity

#company blueprint
companies= Blueprint('companies', __name__,url_prefix='/api/v1/companies')

#creating companies
@companies.route('/create',methods=['POST'])
@jwt_required()
def createCompany():

    #storing request values
    data = request.json
    name = data.get('name')
    origin = data.get('origin')
    description = data.get('description')
    user_id = get_jwt_identity()

    #validations of the incoming request
    if not name or not origin or not description:
        return jsonify({'error':'All fields are required'}),HTTP_400_BAD_REQUEST

    if Company.query.filter_by(name=name).first() is not None:
        return jsonify({'error':'Company name already in use'}),HTTP_400_BAD_REQUEST
    
    try:

       #creating a new company
        new_company = Company(name=name,description=description,origin=origin,user_id=user_id)
        db.session.add(new_company)
        db.session.commit()

        return jsonify({
            'message': name + ' has been created successfully as an ',
            'company':{
                'id':new_company.id,
                'name':new_company.name,
                'origin':new_company.origin,
                'description':new_company.description,

            }
            }),HTTP_201_CREATED 

    except Exception as e:
        db.session.rollback()
        return jsonify({'error':str(e)}),HTTP_500_INTERNAL_SERVER_ERROR
    
    
   #Getting all companies 
@companies.get('/')
@jwt_required()
def getAllCompanies():
    
    try:

        all_companies = Company.query.all()

        companies_data = []

        for company in all_companies:
            company_info = {
                'id':company.id,
                'name':company.first_name,
                'origin':company.origin,
                'description':company.description,
                'user':{
                     'id':company.id,
                     'first_name':company.first_name,
                     'last_name':company.last_name,
                      'username':company.get_full_name(),
                      'email':company.email,
                      'contact':company.contact,
                      'type':company.user_type,
                      'biography':company.biography,
                      'created_at':company.user.created_at
                },
                'created_at':company.created_at
                
            }
            companies_data.append(company_info)


        return jsonify({
            "message":"All companies retrieved successfully",
            "total_companies": len(companies_data),
            "companies": companies_data

            

        }),HTTP_200_OK
             

    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR
    
    #Get company by id
@companies.get('/company/<int:id>')
@jwt_required()
def getCompany(id):

    try:

        company = Company.query.filter_by(id=id).first()
        
        if not company:
            return jsonify({"error":"Company not found"}),HTTP_404_NOT_FOUND

        return jsonify({
            "message":"Company details retrieved successfully",
        
            "company":{
                     'id':company.id,
                     'name':company.first_name,
                      'origin':company.origin,
                      'description':company.description,
                     'user':{
                     'id':company.id,
                     'first_name':company.first_name,
                     'last_name':company.last_name,
                      'username':company.get_full_name(),
                      'email':company.email,
                      'contact':company.contact,
                      'type':company.user_type,
                      'biography':company.biography,
                      'created_at':company.user.created_at
                },
                'created_at':company.created_at
            }

        }),HTTP_200_OK
             
    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR
    
    
 #update company details
@companies.route('/edit/<int:id>',methods=['PUT','PATCH'])
@jwt_required()
def updateCompanyDetails(id):

    try:

        current_user = get_jwt_identity()
        loggedInUser = User.query.filter_by(id=current_user).first()
         
         #get company by id
        company = Company.query.filter_by(id=id).first()

        if not company:
            return jsonify({"error":"Company not found"}),HTTP_404_NOT_FOUND
        
        elif loggedInUser.user_type!='admin' and company.user_id!=current_user:
            return jsonify({'error':'You are not authorised to update the company details'}),HTTP_403_FORBIDDEN
        
        else:
             #Store request data
             name = request.get_json().get('name',company.name)
             origin = request.get_json().get('origin',company.origin)
             description = request.get_json().get('description',company.description)

             company.name = name
             company.origin = origin
             company.description = description
             
             db.session.commit()
             
             return jsonify({
                'message':name + " 's details have been successfully updated",
                "company":{
                     'id':company.id,
                     'name':company.first_name,
                     'origin':company.origin,
                     'description':company.description,
                     'user':{
                     'id':company.id,
                     'first_name':company.first_name,
                     'last_name':company.last_name,
                     'username':company.get_full_name(),
                     'email':company.email,
                     'contact':company.contact,
                     'type':company.user_type,
                     'biography':company.biography,
                     'created_at':company.user.created_at
                },
                'created_at':company.created_at  
                 }
             })

    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR
    

     #Deleting a company
@companies.route('/delete/<int:id>',methods=['DELETE'])
@jwt_required()
def deleteCompany(id):

    try:
        current_user = get_jwt_identity()
        loggedInUser = User.query.filter_by(id=current_user).first()
         
         #get company by id
        company= Company.query.filter_by(id=id).first()

        if not company:
            return jsonify({"error":"Company not found"}),HTTP_404_NOT_FOUND
        
        elif loggedInUser.user_type!='admin' and company.user_id!=current_user: 
            return jsonify({'error':'You are not authorised to delete the company details'}),HTTP_403_FORBIDDEN
        
        else:

            #delete the associated books
            for book in company.books:
                db.session.delete(book)

            db.session.delete(company)
            db.session.commit()


            return jsonify({'message':'Company has been deleted successfully'})
            

    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR
    
    
    
    
    
