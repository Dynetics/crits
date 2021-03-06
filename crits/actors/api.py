try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from tastypie import authorization
from tastypie.authentication import MultiAuthentication

from crits.actors.actor import Actor, ActorIdentifier
from crits.actors.handlers import add_new_actor, add_new_actor_identifier
from crits.core.api import CRITsApiKeyAuthentication, CRITsSessionAuthentication
from crits.core.api import CRITsSerializer, CRITsAPIResource

from crits.vocabulary.acls import ActorACL


class ActorResource(CRITsAPIResource):
    """
    Class to handle everything related to the Actor API.

    Currently supports GET and POST.
    """

    class Meta:
        object_class = Actor
        allowed_methods = ('get', 'post', 'patch')
        resource_name = "actors"
        ordering = ("name", "description", "modified", "status", "id")
        authentication = MultiAuthentication(CRITsApiKeyAuthentication(),
                                             CRITsSessionAuthentication())
        authorization = authorization.Authorization()
        serializer = CRITsSerializer()

    def get_object_list(self, request):
        """
        Use the CRITsAPIResource to get our objects but provide the class to get
        the objects from.

        :param request: The incoming request.
        :type request: :class:`django.http.HttpRequest`
        :returns: Resulting objects in the specified format (JSON by default).

        """

        return super(ActorResource, self).get_object_list(request, Actor)

    def obj_create(self, bundle, **kwargs):
        """
        Handles creating Actors through the API.

        :param bundle: Bundle containing the information to create the Actor.
        :type bundle: Tastypie Bundle object.
        :returns: HttpResponse object.
        """

        user = bundle.request.user
        data = bundle.data
        name = data.get('name', None)
        aliases = data.get('aliases', '')
        description = data.get('description', None)
        source = data.get('source', None)
        reference = data.get('reference', None)
        method = data.get('method', None)
        tlp = data.get('tlp', "amber")
        campaign = data.get('campaign', None)
        confidence = data.get('confidence', None)
        bucket_list = data.get('bucket_list', None)
        ticket = data.get('ticket', None)

        if user.has_access_to(ActorACL.WRITE):
            result = add_new_actor(name,
                                   aliases,
                                   description=description,
                                   source=source,
                                   source_method=method,
                                   source_reference=reference,
                                   source_tlp=tlp,
                                   campaign=campaign,
                                   confidence=confidence,
                                   user=user,
                                   bucket_list=bucket_list,
                                   ticket=ticket)
        else:
            result = {'success':False,
                      'message':'User does not have permission to create Object.'}


        content = {'return_code': 0,
                   'type': 'Actor',
                   'message': result.get('message', ''),
                   'id': result.get('id', '')}
        if result.get('id'):
            url = reverse('api_dispatch_detail',
                          kwargs={'resource_name': 'actors',
                                  'api_name': 'v1',
                                  'pk': result.get('id')})
            content['url'] = url
        if not result['success']:
            content['return_code'] = 1
        self.crits_response(content)

class ActorIdentifierResource(CRITsAPIResource):
    """
    Class to handle everything related to the Actor Identifier API.

    Currently supports GET and POST.
    """

    class Meta:
        object_class = ActorIdentifier
        allowed_methods = ('get', 'post')
        resource_name = "actoridentifiers"
        authentication = MultiAuthentication(CRITsApiKeyAuthentication(),
                                             CRITsSessionAuthentication())
        authorization = authorization.Authorization()
        serializer = CRITsSerializer()

    def get_object_list(self, request):
        """
        Use the CRITsAPIResource to get our objects but provide the class to get
        the objects from.

        :param request: The incoming request.
        :type request: :class:`django.http.HttpRequest`
        :returns: Resulting objects in the specified format (JSON by default).

        """
        user = request.user

        if user.has_access_to(ActorACL.ACTOR_IDENTIFIERS_READ):
            return super(ActorIdentifierResource, self).get_object_list(request,
                                                                        ActorIdentifier)

        else:
            raise NotImplementedError('User does not have permission to view object.')

    def obj_create(self, bundle, **kwargs):
        """
        Handles creating Actor Identifiers through the API.

        :param bundle: Bundle containing the information to create the Actor
                       Identifier.
        :type bundle: Tastypie Bundle object.
        :returns: HttpResponse object.
        """

        user = bundle.request.user
        data = bundle.data
        identifier_type = data.get('identifier_type', None)
        identifier = data.get('identifier', None)
        source = data.get('source', None)
        reference = data.get('reference', None)
        method = data.get('method', None)
        tlp = data.get('tlp', None)

        if user.has_access_to(ActorACL.ACTOR_IDENTIFIERS_ADD):
            result = add_new_actor_identifier(identifier_type,
                                              identifier,
                                              source=source,
                                              source_method=method,
                                              source_reference=reference,
                                              source_tlp=tlp,
                                              user=user)

        else:
            result = {'success':False,
                      'message':'User does not have permission to create Object.'}

        content = {'return_code': 0,
                   'type': 'ActorIdentifier',
                   'message': result.get('message', ''),
                   'id': result.get('id', '')}
        if result.get('id'):
            url = reverse('api_dispatch_detail',
                          kwargs={'resource_name': 'actoridentifiers',
                                  'api_name': 'v1',
                                  'pk': result.get('id')})
            content['url'] = url
        if not result['success']:
            content['return_code'] = 1
        self.crits_response(content)
